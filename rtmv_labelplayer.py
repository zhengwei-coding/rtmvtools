#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   rtmv_labelplayer.py
@Time    :   2021/02/06 21:16:19
@Author  :   Zhengwei GUAN @ SIBITU
@Contact :   zhengwei.guan@hotmail.com; zhengwei.guan@insmapper.com
@Desc    :   player implementation based on QLabel
'''


import sys, os, time, threading, io
from typing import Union
import subprocess as sp
from enum import Enum
import queue
from fractions import Fraction


from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, Signal
import av

from rtmvfile import RtmvParser, RtmvVidPayloadFeeder, RtmvPayloadSection

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RtmvVideoPlayer(QLabel):
    '''
    RtmvVideoPlayer is desinged to play video and image payload of RTMV file
    based on QT Label widget
    '''
    # FIXME:
    # qt image format can be from a lookup table for better flexibility
    _QIMAGE_PIX_FMT = QImage.Format_RGB888

    class State(Enum):
        STOPPED = 0  # Question: what if I don't assign a value to an enum member?
        PLAYING = 1
        PAUSE   = 2

    # QT style implementation of status monitoring interface
    # You should handle the signals below for status subscription
    sectionLoadStatusChanged = Signal(RtmvPayloadSection)
    playerPlayingStatusChanged = Signal(State)
    playingProgressChanged = Signal(float)
    _playingDecodingStopped = Signal(int)

    def __init__(self, parent, payload_sec: RtmvPayloadSection=None):
        super(RtmvVideoPlayer, self).__init__(parent)

        self._stat = RtmvVideoPlayer.State.STOPPED
        self._speed = Fraction(0, 4)  # 0.5, 1, x2, x4

        self._feeder = None  # the feeder instance
        self._frame_queue = None

        self._decode_thread = None
        self._info_thread = None

        self._payload_sec = None
        if payload_sec is not None:
            self.loadSection(payload_sec)

        self._cur_playtime = 0
        self._playingDecodingStopped.connect(self.stop)

        # FIXME: Set up logging level of av, should be done with settings
        av.logging.set_level(av.logging.FATAL)

    def _feederCallback(self, event, args: list=None):
        if event == RtmvVidPayloadFeeder.Event.FINISHED:
            # The orignial idea is to stop playing after the feeder finishes
            # the feeding. However, because of buffer mechanism, feeder usually
            # finishes feeding data much earlier than decoding done. An extreme
            # example is to play a very short video clip. When the feeder done
            # with pumping data in, the player hasn't even started to decode!
            # So the call to stop method is removed here.
            pass
            # self.stop()  # stop the playing

    ''' IMPROVE ME:
        After some effort on exprements for video playing using ffmpeg,
        I eventually choose pyav as python wrapper of ffmpeg as it is more
        flexible than ffmpeg-python, which is a pure wrapper to ffmpeg command
        line. Some limitations are still there, though. I met some trouble in
        pumping data into ffmpeg, including both ffmpeg-python and pyav. After
        some testing done, I eventually chose socket as the data tunnel to ffmpeg
        other than pipe and queue.Queue. The pipe and queue implementation was
        removed then.
    '''
    def _vidDecode(self):
        ct = self._ct

        # TODO: This is for those weired DJI non-I frame stream
        # don't understand why a video stream only contain P frames. It's should be a
        # setting item.
        ct.streams[0].codec_context.flags2 |= av.codec.context.Flags2.SHOW_ALL

        # FIXME: One of purpose of splitting decoding into demux and decoding is to skip
        # packets instead of frames whenever needed.However, it seems that pyav doesn't
        # expose non-reference frame flag for packets (none for frame duration). So dropping
        # packets will cause mosaic as cannot identify packets containing non-reference
        # frames. Better re-build pyav with this change in.

        # Get first packet and frame
        packets = ct.demux(video = 0)
        fr_cnt = 0

        def _decodeFirstFrame(packets):
            fr = None
            duration = 0
            fake_pts = False
            pkt_cnt = 0
            try:
                while True:
                    # Find the first frame
                    pkt = next(packets)  # The first valid packets
                    pkt_cnt += 1
                    duration += pkt.duration * pkt.time_base  # in sec
                    if pkt.dts is None and pkt.pts is None:
                        # No pts in the stream
                        fake_pts = True
                        pkt.dts = 0
                        pkt.pts = 0
                    frames = pkt.decode()
                    if len(frames) > 0:
                        fr = frames[0]
                        break
            except StopIteration:
                # No valid packets found in the stream
                logger.info('No valid packets found in the stream.')
            except EOFError:
                logger.warning('Got EOF error from pkt.decode().')

            return fr, duration, fake_pts, pkt, pkt_cnt

        # FIXME:
        fr, duration, fake_pts, pkt , pkt_cnt = _decodeFirstFrame(packets)
        if fr is not None:  # no frame found
            start_time = time.time()
            first_fr_time = fr.time
            fr_time_abs = start_time
            # The total duration in sec, extract from packet
            self._cur_playtime += duration
            pkt_real_duration = duration * self._speed
            total_duration = pkt_real_duration
            fr_cnt = 1

            # Create frame queue and start the rendering thread
            fr_queue = queue.Queue(10)  # FIXME: max frames should be configurable
            self._decoding = True
            refresh_thread = threading.Thread(target = self._frameRefresh,
                                                name='Frame Refresh', args=[fr_queue])
            refresh_thread.start()

            while self._stat == self.State.PLAYING:
                if fr is not None:
                    fr_queue.put((fr, fr_time_abs, pkt_real_duration))
                try:
                    pkt = next(packets)
                    pkt_cnt += 1

                    # FIXME: This part is tricky and hard to understand (for me)
                    # better implementation?
                    pkt_duration =  pkt.duration * pkt.time_base  # durating in sec
                    pkt_real_duration = pkt_duration * self._speed  # duration in sec with _speed
                    total_duration += pkt_real_duration # Real duration of this packet

                    # Update current overall postion
                    self._cur_playtime += pkt_duration  # This is more like a playback position than a time
                    # FIXME: Update per X packets, X can be a setting item
                    if pkt_cnt % 10 == 0:
                        self.playingProgressChanged.emit(self._cur_playtime)

                    if fake_pts:
                        pkt.dts =  int(total_duration / pkt.time_base)
                        pkt.pts = pkt.dts
                    frames = pkt.decode()
                    if len(frames) > 0:
                        fr_cnt += 1
                        fr = frames[0]
                        fr_time_abs = start_time + (fr.time - first_fr_time)
                    else:
                        fr = None  # no valid frame decoded
                except StopIteration:
                    logger.info('End of video decoding.')
                    break
            # End of decoding, wait for refresh thread to quit
            self._decoding = False
            refresh_thread.join()
            logger.info(f'Done with decoding, {fr_cnt} frames presented @ average '
                        f'frame rate {(fr_cnt)/(time.time()-start_time):.2f}fps')
            # TODO: safe stop here?
        else:
            logger.info('Fail to decode data.')

        self._playingDecodingStopped.emit(fr_cnt)

        '''
        # This is the framerate version implementation.
        # It cannot deal with variable framerate but the implementation is simpler.
        frames = ct.decode()
        frame = next(frames)  # The first frame
        start_time = time.time()
        fr_dur = float(1/ct.streams.video[0].average_rate)  # read from the stream
        next_fr_time = start_time
        skip_next = False
        fr_cnt = 1
        if frame.pts is None:  # There is no pts in this stream
            while self._stat == self.State.PLAYING:
                # Present the first frame
                if skip_next == 0:
                    if frame.format.name != 'rgb24':
                        frame = frame.to_rgb()
                    plane = frame.planes[0]
                    # FIXME: Note that variable 'buf' below is necessary
                    # if I put 'plane.to_bytes()' in line of QImage, the app will
                    # hang! seems caused by GC mechanism (a bug in QImage?)
                    buf = plane.to_bytes()
                    img = QImage(buf, plane.width, plane.height, plane.line_size, self._QIMAGE_PIX_FMT)
                    img = img.scaled(self.width()-self.lineWidth()*2-2,
                                            self.height()-self.lineWidth()*2-2,
                                            Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.setPixmap(QPixmap(img))
                    # logger.debug(f'frame is presented @ {next_fr_time}!!!  ------[{frame.index:>05}:{frame.pict_type}]------')
                else:
                    logger.debug(f'frame is skipped for catching up------[{frame.index:>05}:{frame.pict_type}]------')
                    skip_next -= 1
                try:
                    frame = next(frames)
                    fr_cnt += 1
                except StopIteration:  # end of decoding
                    break
                if self._speed > 0:  # otherwise no control
                    delta = fr_dur*self._speed
                    next_fr_time += delta
                    if skip_next == 0:
                        delay = next_fr_time - time.time()
                        if delay > 0.005:  # add some tolerence other than 0.0s
                            time.sleep(delay)
                        elif delay <= -delta:
                            skip_next = int(abs(delta//delay)) + 1  # skip n frame to catch up

        else:  # TODO: for pts based handling
            pass

        logger.info(f'Done with decoding, {fr_cnt} frames presented @ average '
                    f'frame rate {(fr_cnt)/(time.time()-start_time):.2f}fps')
        '''

    # TODO: That would be better to put rendering & decoding in separated threads to
    # make sure deocoding is not somehow blocked. Also a frame queue is used for smooth
    # frame dropping.
    def _frameRefresh(self, frame_queue: queue.Queue):
        pix_swap = [None, None]
        pix_index = 0
        lastframe_skipped = False
        skip = 0
        while self._decoding:
            try:
                fr, present_time, duration = frame_queue.get_nowait()
                if skip > 0 and not lastframe_skipped:
                    skip -= 1
                    lastframe_skipped = True
                    continue
                delay = present_time - time.time()
                if int(self._speed) != 0:
                    if delay > 0.005:
                        skip = 0
                        time.sleep(delay)
                    # FIXME: this shall be the duration of next frame actually.
                    elif delay <= -duration:
                        # skip n packets to catch up
                        skip = int(abs(delay//duration)) - 1
                        lastframe_skipped = True
                        logger.debug(f'skip {skip} packets to catch up')
                        continue
                # Render the frame
                if fr.format.name != 'rgb24':
                    fr = fr.to_rgb()
                # TODO: no handling for interlaced video, progressive only
                plane = fr.planes[0]
                # FIXME: Note that variable 'buf' below is necessary
                # if I put 'plane.to_bytes()' in line of QImage, the app will
                # hang! seems caused by GC mechanism (a bug in QImage?)
                buf = plane.to_bytes()
                img = QImage(buf, plane.width, plane.height, plane.line_size, self._QIMAGE_PIX_FMT)

                # FIXME: Would like to setScaledContents(True) but it somehow doesn't work.
                # it's said it doesn't work with a label in a layout but I can't find it in official QT docs.
                # setScaledContent seems to make app unstable especially when you move the window rapidly with video
                # playing, why?
                # And current resizing the playing video will cause some weired behavior, yet to dig in.

                # FIXME: it seems there is something wrong with QLabel.setPixmap(pix:QPixmap)
                # when pix is released (most likely due to garbage collection mechanism) before
                # next setPixmap called, it is easy to make the app hang (especially when you resize the video)!
                #  That is why a two-member list is set for swap.

                # FIXME: don't trust self.width()-self.lineWidth()*2, it causes very weired behavior while playing.
                # It seems that QLabel will resize to contain the pixmap if you set a pixmap with a size bigger than
                # the QLabel. maybe due to setScaledContent only can be false?
                # scale pixmap to fit the label
                img = img.scaled(self.width()-self.lineWidth()*2-2,
                                        self.height()-self.lineWidth()*2-2,
                                        Qt.KeepAspectRatio, Qt.SmoothTransformation)
                pix_swap[pix_index] = QPixmap(img)
                self.setPixmap(pix_swap[pix_index])
                # self.setText(f'frame index:{fr.index}\nframe size:{fr.width}x{fr.height}\nframe type:{fr.pict_type}')
                pix_index = 0 if pix_index == 1 else 1
            except queue.Empty:
                logger.debug('Empty frame queue, wait 0.01s and try again')
                time.sleep(0.01)
                continue

    def loadSection(self, payload_sec: RtmvPayloadSection=None):
        if self._payload_sec is not None:
            self.freeSection()
        self._payload_sec = payload_sec
        self.sectionLoadStatusChanged.emit(self._payload_sec)

    def play(self, payload_sec: RtmvPayloadSection=None):
        if payload_sec is not None:
            self.loadSection(payload_sec)

        if self._stat == RtmvVideoPlayer.State.PLAYING: return
        if self._stat == RtmvVideoPlayer.State.PAUSE:
            self.resume()
            return

        # start the feeder thread with socket model
        self._feeder = RtmvVidPayloadFeeder(
            self._payload_sec.rt, self._payload_sec.start, self._payload_sec.end,
            tuple((None, None)), None, # callback = self._feederCallback,
            autostart = True
            )

        # set up the av
        addr = f'tcp://{self._feeder.hostaddr[0]}:{self._feeder.hostaddr[1]}'
        try:
            self._ct = av.open(addr, mode='r')
            self._stat = RtmvVideoPlayer.State.PLAYING
            self.playerPlayingStatusChanged.emit(RtmvVideoPlayer.State.PLAYING)
            self._decode_thread = threading.Thread(target=self._vidDecode,
                                                    name='Video Decoding',
                                                    args=[])

            self._decode_thread.start()
        except av.error.InvalidDataError:
            self._feeder.stop()
            logger.warning(f'Fail to open container {addr}')
            return

    def pause(self):
        if self._stat == RtmvVideoPlayer.State.PLAYING:
            self._feeder.pause()
            self._stat = RtmvVideoPlayer.State.PAUSE
            self._decode_thread.join()
            self.playerPlayingStatusChanged.emit(RtmvVideoPlayer.State.PAUSE)

    def resume(self):
        if self._stat == RtmvVideoPlayer.State.PAUSE:
            self._feeder.resume()
            self._stat = RtmvVideoPlayer.State.PLAYING
            self._decode_thread = threading.Thread(target=self._vidDecode,
                                        name='Video Decoding',
                                        args=[])
            self._decode_thread.start()
            self.playerPlayingStatusChanged.emit(RtmvVideoPlayer.State.PLAYING)

    def skip(self, pos):
        pass

    def stop(self, fr_cnt: int=None):
        if fr_cnt is not None:
            logger.debug(f'This is a natural stop call fr_cnt = {fr_cnt}')
        if self._stat == RtmvVideoPlayer.State.PLAYING or self._stat == RtmvVideoPlayer.State.PAUSE:
            self._stat = RtmvVideoPlayer.State.STOPPED

            # FIXME: stop rendering BEFORE stopping the feeder, otherwise
            # feeder thread might wait at sending bytes, deadlock heapens
            # how to make it safer?
            self._decode_thread.join()
            self._decode_thread = None
            self._info_thread = None
            self._ct.close()

            # Stop the feeder
            if self._feeder.status != RtmvVidPayloadFeeder.State.IDLE:
                self._feeder.stop()
            # FIXME: No need to release feeder, can simply leave it there
            # self._feeder = None

            # clear the content
            self.clear()

            # TODO: Others (?)
            self._cur_playtime = 0
            self.playerPlayingStatusChanged.emit(RtmvVideoPlayer.State.STOPPED)
        else:
            logger.warning('Player status is set to STOPPED before player.stop()')

    def freeSection(self):
        if self._stat != self.State.STOPPED:
            self.stop()
        self._payload_sec = None
        self.sectionLoadStatusChanged.emit(None)

    @property
    def stat(self):
        return self._stat

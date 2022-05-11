# -*- coding: utf-8 -*-
"""
@author: Zhengwei GUAN
"""

# player implementation based on QLabel

import sys, os, time, threading, io
import subprocess as sp
from enum import Enum
import queue

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
import ffmpeg
import av

from rtmvfile import RtmvParser, RtmvVidPayloadFeeder

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(message)s')
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RtmvVideoPlayer(QLabel):
    '''
    RtmvVideoPlayer is desinged to play video and image payload of RTMV file
    based on QT Label widget
    '''
    # FIXME: ffmpeg pix format can be a setting item
    # pix bytes and qt image format can be from a lookup table for better flexibility
    _FFMPEG_PIX_FMT = 'rgb24'
    _FFMPEG_PIX_BYTES = 3
    _QIMAGE_PIX_FMT = QImage.Format_RGB888

    class State(Enum):
        STOPPED = 0  # Question: what if I don't assign a value to an enum member?
        PLAYING = 1
        PAUSE   = 2

    def __init__(self, parent, rt: RtmvParser=None, payload_sec: RtmvParser.PayloadSection=None):
        super(RtmvVideoPlayer, self).__init__(parent)

        self._rt = rt
        self._payload_sec = payload_sec
        self._stat = RtmvVideoPlayer.State.STOPPED

        self._proc = None  # decoding process
        self._feeder = None  # the feeder instance
        self._frame_queue = None

        self._refresh_thread = None
        self._info_thread = None

    def _feederCallback(self, event, args: list=None):
        if event == RtmvVidPayloadFeeder.Event.FINISHED:
            self.stop()  # stop the playing

    def _refreshFrame(self):
        frame_grabber = self._frameGrabber()
        frame_cnt = -1
        try:
            start_time = time.time()
            pix = [None, None]
            frame_grabber.send(None)
            while self._stat != self.State.STOPPED:
                try:
                    # frame = self._frame_queue.get(timeout = 0.03)

                    # frame_pixmap = next(frame_grabber)
                    frame = {'s': '1920x1440'}
                    frame_pixmap = frame_grabber.send(frame)
                    # TODO: Update OSD (if needed)
                    # self.setText(f"frame number={frame['n']}\nPTS={frame['pts']}\nPTSTIME={frame['pts_time']}\nFrameType={frame['type']}")

                    # FIXME: Would like to setScaledContent(True) but it somehow doesn't work.
                    # it's said it doesn't work with a label in a layout but I can't find it in official QT docs.
                    # setScaledContent seems to make app unstable especially when you move the window rapidly with video
                    # playing, why?

                    # FIXME: it seems there is something wrong with QLabel.setPixmap(pix:QPixmap)
                    # when pix is released (most likely due to garbage collection mechanism) before
                    # next setPixmap called, it is easy to make the app hang!

                    # scale pixmap to fit the label
                    # FIXME: don't trust self.width()-self.lineWidth()*2, it causes very weired behavior while playing.
                    # It seems that QLabel will resize to contain the pixmap if you set a pixmap with a size bigger than
                    # the QLabel. maybe due to setScaledContent only can be false?
                    if frame_pixmap is not None:
                        frame_cnt += 1
                        pix[frame_cnt%2] = QPixmap(frame_pixmap.scaled(
                                                        self.width()-self.lineWidth()*2-2,
                                                        self.height()-self.lineWidth()*2-2,
                                                        Qt.KeepAspectRatio
                                                        )
                                                    )
                        self.setPixmap(pix[frame_cnt%2])
                        # time.sleep(0.001)
                except queue.Empty:
                    # logger.debug('Queue is empty.')
                    # check the feeder
                    time.sleep(0.03)
                    continue
        except StopIteration:
            logger.info('The refresher has got the last frame.')
        logger.info(f'Quit frame refresher - average framerate is {frame_cnt / (time.time()-start_time)}')

    # this is a test to try generator mode, doesn't work well
    def _frameGrabber(self):
        try:
            img = None
            w, h = 0, 0
            # FIXME: should that be while True or while condition?
            while self._stat != self.State.STOPPED:
                frame_info = yield img
                if frame_info is not None:
                    w, h = (int(i) for i in frame_info['s'].split('x'))
                    frame = self._proc.stdout.read(w*h*self._FFMPEG_PIX_BYTES)
                    if frame != b'':
                        img = QImage(frame, w, h, w*self._FFMPEG_PIX_BYTES, self._QIMAGE_PIX_FMT)
                else:
                    return
        except ValueError:
            logger.info('file closed by another thread.')

    '''
        below is the structure of frame info (extract from ffmpeg showinfo filter)
            'n':'0'
            'pts':'672000'
            'pts_time':'0.56'
            'pos':'242505'
            'fmt':'yuv420p'
            'sar':'0/1'
            's':'1088x720'
            'i':'P'
            'iskey':'1'
            'type':'I'
            'checksum':'5FFD8848'
            'plane_checksum':'[BFB7D7CE1ABC2DD53AA98296]'
            'mean':'[106132123\x08]'
            'stdev':'[48.3 8.2 6.7 \x08]'
    '''
    def _refreshFrameInfo(self):
        with open('log.txt', 'w') as f:
            showinfo = []
            new_lines = []
            tail = ''
            # frame_grabber = self._frameGrabber()
            try:
                while self._stat != self.State.STOPPED:
                    if self._proc.poll() is None:
                        err = self._proc.stderr.read1()
                    else:
                        logger.debug(f'ffmpeg quit with error code {self._proc.returncode}')
                        print(showinfo)

                    # replace \r with \n because 'frame info' line of ffmepg stderr ending with \r
                    # which complicates info parsing
                    new_lines = (tail + err.decode('utf-8')).replace('\r', '\n').splitlines(True)
                    tail = ''
                    for line in new_lines:
                        if line[-1] != '\n':  # last line and uncomplete
                            tail = line
                            break
                        else:
                            showinfo.append(line)
                        if line.startswith('[Parsed_showinfo') and '] n:' in line:
                            # next(frame_grabber) -> not safe, cause the pipe deadlock (why?)
                            # line = line[line.find('n:') : line.find('pos:')].split(' ')
                            # FIXME: should be implemented with re???? current impl is awkward and unsafe
                            frameinfo = {}
                            while line.find(':') != -1:
                                pos = line.find(':')
                                key = line[:pos].strip().split(' ')[-1]
                                line = line[pos+1:]
                                pos2 = line.find(':')
                                if pos2 == -1:
                                    value = line.strip()
                                else:
                                    value = ''.join(line[:pos2].strip(' ').split(' ')[:-1])
                                frameinfo[key] = value
                            self._frame_queue.put(frameinfo)
                        elif line.strip().startswith('frame='):
                            logger.debug(line)

            except ValueError:
                logger.info('stderr is closed by another thread')

            logger.info('Quit frame info thread')

    def play(self, rt: RtmvParser=None, payload_sec: RtmvParser.PayloadSection=None):
        if rt is not None: self._rt = rt
        if payload_sec is not None: self._payload_sec = payload_sec

        if self._stat == RtmvVideoPlayer.State.PLAYING: return
        if self._stat == RtmvVideoPlayer.State.PAUSE:
            pass  # resume the playing
        '''
        # start to play
        self._proc = (
            ffmpeg
            .input('pipe:')
            #.filter('probesize', '10M')
            # use the following two filter to fast forward and slow motion
            #.setpts('2*PTS')
            #.filter('fps', fps=1, round='up')
            .filter('showinfo')
            .output('pipe:', format='rawvideo', pix_fmt=self._FFMPEG_PIX_FMT)
            .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
        )
        '''
        # ['ffmpeg', '-i', 'pipe:', '-filter_complex', '[0]showinfo[s0]', '-map', '[s0]', '-f', 'rawvideo', '-pix_fmt', 'rgb24', 'pipe:']
        cmd = [
                'ffmpeg',
                '-hide_banner',
                '-report',
                '-probesize', '50000000',
                '-i', 'pipe:',
                '-flags2', 'showall',
                '-filter_complex', '[0]showinfo[s0]',
                '-map', '[s0]',
                '-f', 'rawvideo',
                '-pix_fmt', self._FFMPEG_PIX_FMT,
                'pipe:'
            ]
        self._proc = sp.Popen(cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)

        self._feeder = RtmvVidPayloadFeeder(
            self._rt, self._payload_sec.start, self._payload_sec.end,
            self._proc.stdin, callback = self._feederCallback,
            autostart = True
            )
        self._stat = RtmvVideoPlayer.State.PLAYING

        self._frame_queue = queue.Queue()
        self._refresh_thread = threading.Thread(target=self._refreshFrame, name='Frame Refresher', args=[])
        self._info_thread = threading.Thread(target=self._refreshFrameInfo, name='FrameInfo Puller', args=[])

        self._refresh_thread.start()
        self._info_thread.start()

    def pause(self):
        if self._stat == RtmvVideoPlayer.State.PLAYING:
            self._feeder.pause()
            self._stat == RtmvVideoPlayer.State.PAUSE

    def stop(self):
        if self._stat == RtmvVideoPlayer.State.PLAYING or self._stat == RtmvVideoPlayer.State.PAUSE:
            '''
                TODO: stopping process (for ffmpeg): very tricky
                1. close the stdout and stderr, otherwise the app has chance to hang (in stdout/stderr thread)
                2. terminate the decoding process, otherwise the feeder thread might hang (in stdin writing)
                3. stop the feeder
                4. close the stdin (somehow feeder might hang if stdin is closed prior to feeder stops)
            '''
            self._stat = RtmvVideoPlayer.State.STOPPED

            # make sure decoding process stopped
            if self._proc.poll() is None:
                self._proc.terminate()
            self._proc.wait()
            logger.debug('process finished')

            self._proc.stdout.close()
            self._proc.stderr.close()

            # Stop the feeder
            if self._feeder.status != RtmvVidPayloadFeeder.State.IDLE:
                self._feeder.stop()
            # FIXME: No need to release feeder, can simply leave it there
            # self._feeder = None
            logger.debug('feeder stopped')
            try:
                self._proc.stdin.close()
            except OSError:
                # catch this once don't know why,
                # never re-produce it again by repeatly play / stop
                logger.warning(f'OSError when trying to stop stdin {self._proc.stdin}')

            # TODO: stop rendering
            self._info_thread.join()
            self._refresh_thread.join()
            self._refresh_thread = None
            self._info_thread = None

            # clear the content
            self.clear()

            self._proc = None

            # TODO: Others (?)
            pass

    def freeSection(self):
        if self._stat != self.State.STOPPED:
            self.stop()

        self._rt = None
        self._payload_sec = None

    def getStat(self):
        return self._stat

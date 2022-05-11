#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   rtmvfile.py
@Time    :   2021/02/06 21:17:33
@Author  :   Zhengwei GUAN @ SIBITU
@Contact :   zhengwei.guan@hotmail.com; zhengwei.guan@insmapper.com
@Desc    :   This is a parser to rtmv files
'''

import os, sys, io
import struct
import queue
from collections import namedtuple
from enum import Enum, unique
import time
import subprocess as sp
import threading
import socket

import json
import av

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(funcName)s - %(message)s')
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

class RtmvParser(object):
    # the protocol: ("field name", len in bytes, type)
    _big_little = '!' # '<' for little endien while '!' for big
    protocol_sig = 'PaVE' #signature must be ascii encoded
    if _big_little == '<':
        protocol_sig = protocol_sig[::-1]

    # protocol_sig = 'EVaP'
    Field = namedtuple('Field', ['name','len', 'type'])
    protocol = (Field("Signature", len(protocol_sig), "s"),      \
                Field("Ver", 1, "b"),              \
                Field("Ctrl_quality", 1, "b"),     \
                Field("Vid_quality", 1, "b"),      \
                Field("header_size", 1, "B"),      \
                Field("timestamp", 8, "d"),     \
                Field("mission_state", 4, "f"),  \
                Field("VelocityX", 4, "f"),      \
                Field("VelocityY", 4, "f"),      \
                Field("VelocityZ", 4, "f"),      \
                Field("lat", 8, "d"),           \
                Field("long", 8, "d"),          \
                Field("alt", 4, "f"),            \
                Field("height", 4, "f"),         \
                Field("hdop_h", 4, "f"),         \
                Field("hdop_v", 4, "f"),         \
                Field("satCount", 4, "i"),         \
                Field("uav_roll", 4, "f"),       \
                Field("uav_pitch", 4, "f"),      \
                Field("uav_yaw", 4, "f"),        \
                Field("cam_roll", 4, "f"),       \
                Field("cam_pitch", 4, "f"),      \
                Field("cam_yaw", 4, "f"),        \
                Field("payload_size", 4, "i"),     \
                Field("vid_codec", 1, "b"),        \
                Field("frame_type", 1, "b"),       \
                Field("stream_w", 2, "h"),         \
                Field("stream_h", 2, "h"),         \
                Field("disp_w", 2, "h"),         \
                Field("disp_h", 2, "h"),         \
                Field("uav_name", 20, "s"), \
                Field("reserved",2,"s")     \
                 )


    @unique
    class PayloadType(Enum):
        VIDEO = 4
        IMAGE = 1

    RtmvHeader = namedtuple('RtmvHeader', [fe.name for fe in protocol])
    RtmvPackage = namedtuple('RtmvPackage', ['pos','header', 'len'])

    # Use clase instread of name tuple for more flexibility, see class definition underneath
    # the file.
    # PayloadSection = namedtuple('RtmvPayloadSection', ['start', 'end', 'type', 'meta'])

    header_len = sum([fe.len for fe in protocol])

    # FIXME: ugly implementation, there must be a better way
    _payload_offset = 0
    for fe in protocol:
        if fe.name != 'payload_size':
            _payload_offset += fe.len
        else:
            break
    def _getPkgSizeFromBuff(self, pos) -> int:
        payload_len, = struct.unpack(self._big_little+'i',
                self._bytesbuff[pos + self._payload_offset :
                                pos + self._payload_offset + 4])
        return self.header_len + payload_len

    _struct_fmt = _big_little
    for fe in protocol:
        if fe.type == 's': _struct_fmt += str(fe.len)
        _struct_fmt += fe.type

    # initiliation
    def __init__(self, url=''):
        self.free()
        if url != '':
            self.load(url)

    def free(self):
        self._bytesbuff   = b''
        self._file        = None
        self._rtmvpackages = []
        self.rtmv_sync    = []
        self._payload_sec = []
        self._srcurl       = ''
        self._filesize     = 0
        self._vpkg_cnt     = 0
        self._ppkg_cnt     = 0
        self._duration     = 0
        self._starttime    = None
        self._centerpos    = []

    @property
    def payload_sections(self):
        return self._payload_sec

    @property
    def rtmvpackages(self):
        return self._rtmvpackages

    @property
    def duration(self):
        return self._duration

    @property
    def start_time(self):
        return self._starttime

    @property
    def cetner_pos(self):
        return self._centerpos

    @property
    def srcurl(self):
        return self._srcurl

    # load rtmv packages from a rtmv file
    def load(self, url):
        # this is the case for local rtmv file
        if self._file is not None:
            logger.warning('Please release the current rtmv file first.')
            return None
        self._filesize = os.path.getsize(url)
        if self._filesize > 2*1024*1024*1024:
            logger.error(f'file size exceeds the 1G limit: {self._filesize}')
            self._filesize = 0
            return None

        # Load all packages
        with open(url, 'rb') as self._file:
            self._srcurl = url
            self._bytesbuff = self._file.read()
            totalsize = len(self._bytesbuff)
            pos = 0
            # pos = self._bytesbuff.find(self.protocol_sig, pos)
            while totalsize - pos > self.header_len:
                pos = self._bytesbuff.find(self.protocol_sig.encode('utf-8'), pos)
                if pos == -1:
                    break
                if self._isRtmvPackage(pos):
                    self.rtmv_sync.append(pos) # sync once

                    while True:
                        thisheader = RtmvParser.RtmvHeader(*struct.unpack(self._struct_fmt, self._bytesbuff[pos : pos+self.header_len]))
                        self._rtmvpackages.append(RtmvParser.RtmvPackage(pos, thisheader, thisheader.payload_size + self.header_len))
                        if thisheader.vid_codec == 4 : self._vpkg_cnt += 1
                        else: self._ppkg_cnt += 1
                        pos += self._rtmvpackages[-1].len
                        if self._isRtmvPackage(pos) is not True: # no followed sync bytes
                            pos += len(self.protocol_sig)
                            break
                else: # no followed sync bytes
                    pos += len(self.protocol_sig)
                    continue
        if len(self._rtmvpackages) == 0: return # no packages found

        # Load all payload sections
        sec_start = 0
        sec_end = 0
        sec_type = self._rtmvpackages[0].header.vid_codec
        for i, pkg in enumerate(self._rtmvpackages):
            # generate the payload section
            if pkg.header.vid_codec != sec_type: # the current section end
                sec_end = i-1 # set the end for the current label
                self._payload_sec.append(RtmvPayloadSection(self, sec_start, sec_end,
                                                        RtmvParser.PayloadType(sec_type), None))
                sec_start = i
                sec_end = i
                sec_type = pkg.header.vid_codec
        else:
            sec_end = i-1 # reach to the last package, closing the section.
            self._payload_sec.append(RtmvPayloadSection(self, sec_start, sec_end,
                                                        RtmvParser.PayloadType(sec_type), None))

        # TODO: analyze the payload
        for sec in self._payload_sec:
            if sec.type == self.PayloadType.VIDEO:
                # streams = self._probeVideoPkg(sec.start, sec.end)
                # if streams is not None:
                #    sec.meta.update(streams)
                streams = self._probeVideoPkgAv(sec.start, sec.end)
                if streams is not None:
                    sec.meta = streams
            else:
                pass

        # set up meta data of the rtmvfile
        self._starttime = self._rtmvpackages[0].header.timestamp
        self._duration = self._rtmvpackages[-1].header.timestamp - self._starttime
        self._centerpos = [self._rtmvpackages[int(len(self._rtmvpackages)/2)].header.lat,
                            self._rtmvpackages[int(len(self._rtmvpackages)/2)].header.long,
                            self._rtmvpackages[int(len(self._rtmvpackages)/2)].header.alt
                        ]

        return

    def _probeVideoPkgAv(self, pkg_s, pkg_e, probesize = 1000000, retry = -1):
        '''
        video probe implementation by pyav
        '''
        pkgs = tuple(range(pkg_s, pkg_e+1))
        times = 0
        pos = 0
        while pos < len(pkgs):
            times += 1
            buf = b''
            for pkg in pkgs[pos:-1]:
                buf += self.getPayload(pkg)
                if len(buf) > probesize:
                    pos = pkg
                    break

            f_buf = io.BytesIO(buf)
            try:
                ct = av.open(f_buf)
                break
            except av.InvalidDataError:
                if retry == -1 or times < retry:
                    continue
                else:
                    ct.close()
                    return None
        # to simplify the things, we only include codec, size,
        # pixel format and framerate to the metadata of video stream detected
        vid_meta = None
        if len(ct.streams.video) > 0:
            cc = ct.streams.video[0].codec_context
            vid_meta = {'codec': cc.name,
                        'size': f'{cc.width}x{cc.height}',
                        'pix_fmt': cc.pix_fmt,
                        'framerate': cc.framerate
            }
        ct.close()
        return vid_meta

    def getPayloads(self, pkgs:tuple) -> list:
        '''
        get the payload data
        '''
        bufflist = []
        try:
            for i in pkgs:
                pkg = self._rtmvpackages[i]
                bufflist.append(self._bytesbuff[pkg.pos+RtmvParser.header_len : pkg.pos+pkg.len])
        except IndexError:
            logger.error(f'Invalid package index passed in.')
        return bufflist

    def getPayload(self, i:int) -> bytes:
        buf = b''
        pkg = self._rtmvpackages[i]
        return self._bytesbuff[pkg[0]+RtmvParser.header_len : pkg[0]+pkg[2]]

    def getDuration(self, start = 0, end = -1): # get the duration in sec between pkgs (start, end)
        if end > len(self._rtmvpackages): end = -1
        if start > len(self._rtmvpackages): return 0
        return self._rtmvpackages[end].header.timestamp \
                - self._rtmvpackages[start].header.timestamp

    def _isRtmvPackage(self, pos):
        if self._filesize - pos < self.header_len: return False
        if self._bytesbuff[pos : pos + len(self.protocol_sig)].decode() != self.protocol_sig:
            return False

        psize = self._getPkgSizeFromBuff(pos)
        if psize < 0: return False

        if self._filesize - pos == psize: # the last package
            return True
        elif self._filesize - pos < psize + len(self.protocol_sig): # incomplete ending
            return False
        else:
            return self._bytesbuff[pos + psize : pos + psize + len(self.protocol_sig)] == \
                    self.protocol_sig.encode('ascii')

    def getPosFromTime(self, sec) -> int:
        pass # seek to the position where time equals to sec

    # TODO: Using this function ro replace payloadfeeder constructor, to be completed
    def getPayloadFeeder(self, pkg_s, pkg_e, consumer = None, callback=None, autostart=False):
        feeder = RtmvVidPayloadFeeder(self, pkg_s, pkg_e, consumer, callback, autostart)
        self._feeders.append(feeder)
        return feeder

class RtmvVidPayloadFeeder(object):
    class State(Enum):
        IDLE = 0
        SENDING = 1
        PAUSE = 2

    class Event(Enum):
        FINISHED = 0
        FLUSH = 1

    def __init__(self, rt:RtmvParser, pkg_s, pkg_e, io_consumer = None,
                    callback=None, autostart=False):
        self._rt          = rt # the rtmv file
        self._consumer    = io_consumer
        self._pkgs        = tuple(range(pkg_s, pkg_e+1))
        self._thread      = None
        self._sentbytes   = 0
        self._status      = RtmvVidPayloadFeeder.State.IDLE
        self._cur_pkg     = -1

        if callback is not None and callable(callback):
            self._callback = callback # callback when finish the feeding
        else:
            self._callback = None
        if autostart:
            self.start()

    @property
    def status(self):
        return self._status

    @property
    def cur_pkg(self):
        return self._cur_pkg

    @property
    def progress(self):
        if self._cur_pkg >= self._pkgs[0]:
            return (self._cur_pkg - self._pkgs[0]) / len(self._pkgs)
        else:
            return None

    @property
    def hostaddr(self):
        return self._hostaddr

    '''
    # Three implementations were tested against different scenarios.
    # Eventually the socket one was kept as it has more flexibility.
    # pipe version implementation cannot server pyav as it cannot open a file
    # object with a name with a non-str type (should be a bug). Buffer queue
    # version also doesn't serve pyav conveniently. Socket way is more flexible
    # and natively supports to feed to a remote address.
    '''
    def _feedVideoPayloadSocket(self):
        self._cur_pkg = self._pkgs[0]
        # Wait for connection from consumer end
        while self._status == RtmvVidPayloadFeeder.State.SENDING:
            try:
                con, addr = self._socket.accept()
                logger.info(f'Got one connection in. addr:port = {addr[0]}:{addr[1]}')
                break
            except socket.timeout:
                continue

        # Start to feed packages
        time_start = time.time()
        try:
            for self._cur_pkg in self._pkgs:
                if self._status == RtmvVidPayloadFeeder.State.SENDING:
                    buf = self._rt.getPayload(self._cur_pkg)
                    self._sentbytes += con.send(buf)
                    logger.debug(f'write {self._sentbytes} bytes in')
                elif self._status == RtmvVidPayloadFeeder.State.PAUSE:
                    while self._status == RtmvVidPayloadFeeder.State.PAUSE:
                        # wait until status changed
                        time.sleep(0.1)
                    continue
                else:
                    con.close()
                    break
            else:
                con.close()
        # FIXME: specify the exception type
        except Exception as e:
            logger.info(e)  # For debug, catch exception when the socket is closed

        finally:
            self._socket.close()

        self._status = RtmvVidPayloadFeeder.State.IDLE
        self._cur_pkg = -1
        if self._callback is not None:
            self._callback(RtmvVidPayloadFeeder.Event.FINISHED, [self._sentbytes])
            self._callback = None

        logger.info(f'Finish feeding data {self._sentbytes} bytes at average '
                    f'rate {self._sentbytes/(time.time()-time_start):.2f}Bytes per sec')

    def start(self):
        self._sentbytes = 0
        self._status = RtmvVidPayloadFeeder.State.SENDING

        # FIXME: default port should be a setting item
        port = 15000
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TODO: check socket programming
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while True:
            try:
                # FIXME: My intention is to bind to the host ipaddr
                # which is accessible from remote. However, it doesn't work
                # when the host has multiple IP address, which is the most
                # case, I believe. For feeding data to remote consumers, it is
                # more pratical to appoint interface or ipaddress instead of
                # getting names from "gethostname", more study!
                # Also, for consumers behind a NAT, it may be more convenient to
                # work on client mode.
                self._socket.bind(tuple((socket.gethostname(), port)))
                break
            except OSError:  # port number is occupied
                logger.info(f'the port number {port} is occupied, try {port+1}')
                port += 1
                continue
        self._hostaddr = self._socket.getsockname()
        self._socket.listen(1)  # only one connection is allowed
        self._socket.settimeout(5)  # set 5s timeout FIXME: could be a setting item
        target = self._feedVideoPayloadSocket

        self._thread = threading.Thread(target=target, name='Feeder Thread', args=[])
        self._thread.start()

    def stop(self):
        self._status = RtmvVidPayloadFeeder.State.IDLE
        self._thread.join()


    def pause(self):
        self._status = RtmvVidPayloadFeeder.State.PAUSE

    def resume(self):
        self._status = RtmvVidPayloadFeeder.State.SENDING

    def seek(self, percent):
        pass


class RtmvPayloadSection(object):
    def __init__(self, rt: RtmvParser, start: int, end: int, p_type: RtmvParser.PayloadType, meta: dict=None):
        self._rt = rt
        self._start = start
        self._end = end
        self._p_type = p_type
        self._duration = self._rt.getDuration(self._start, self._end)
        self._meta = None if meta is None else dict(meta)

    @property
    def rt(self):
        return self._rt

    @property
    def duration(self):
        return self._duration

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def type(self):
        return self._p_type

    @property
    def meta(self):
        return self._meta

    @meta.setter
    def meta(self, meta: dict):
        self._meta = dict(meta)

if __name__ == "__main__":
    url = ''
    if len(sys.argv) > 1:
        url = sys.argv[1]
    rt = RtmvParser(url)

    '''
    print(len(sys.argv))
    for i in range(len(sys.argv)):
        print('arg: ', sys.argv[i])
    '''

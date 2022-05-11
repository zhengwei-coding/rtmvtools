# -*- coding: utf-8 -*-
"""
@author: Zhengwei GUAN
"""

import sys, os, time, threading

from rtmvfile import RtmvParser
from rtmv_parser_cmd import RtmvParserCmd
# import ffmpeg
import subprocess as sp

def feedVid(p:sp.Popen, size=-1):
    with open("20200903_184548.h264",'rb') as f:
        by = f.read(size)
        len = p.stdin.write(by)
        print(f'------- {len} bytes written -------')
#        p.stdin.flush()
#        p.stdin.close()
    return by

def readResult(p:sp.Popen):
    err = p.stderr.read(1)
    result = p.stdout.read(1)
    print(str(by))
    p.terminate()

if __name__ == '__main__':

    fargs = ['ffprobe', '-show_format', '-show_streams', '-of', 'json', 'pipe:']
    p = sp.Popen(fargs, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, bufsize=10000000)
    threading.Thread(target=feedVid, args=[p, 2000000]).start()
#    out, err = p.communicate(feedVid(p, 2000000))
    
    threading.Thread(target = readResult, args=[p]).start()

    p.wait()
    print('We are Here!')

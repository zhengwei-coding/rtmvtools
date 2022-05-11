# -*- coding: utf-8 -*-
"""
@author: Zhengwei GUAN
"""

# CLI for rtmv parsing

import os, sys
from rtmvfile import RtmvParser
# from inspect import isfunction
import inspect
import getopt
import time

class RtmvParserCmd(object):
    '''
    do not define a class member, functions only
    '''
    def __init__(self, rt: RtmvParser):
        self.rt = rt

    def brief(self, arg: str):
        '''
        Brief: Brief the basic information of loaded rtmv file.
        Usage: brief
        Option: None
        '''
        rt = self.rt
        if (rt is None) | (rt.srcurl == ''):
            print('Please load a rtmv file first.')
            return
        
        print('Basic RTMV file info:')
        print('file name: ',rt.srcurl, ' size: ', rt.filesize)
        print("Sync ", len(rt.rtmv_sync), " times in total at position", rt.rtmv_sync)
        print('Total RTMV packages: ',len(rt.rtmvpackages))
        print('Video RTMV packages: ', rt.vpkg_cnt)
        print('Image RTMV packages: ', rt.ppkg_cnt)
        print('The dataset was acquisited at: {}'.format(time.asctime( time.localtime(rt.starttime))))
        print('The duration of the dataset is {}s'.format(rt.duration))
        print('The rtmv was acquisited around: ({0}, {1}, {2})'.format(rt.centerpos[0], rt.centerpos[1], rt.centerpos[2]))

    def load(self, arg: str):
        '''
        Brief: Load a rtmv file
        Usage: load file_url 
        Option: None
        Example:
            load testdata.rtmv
        '''
        rt = self.rt
        if arg == '':
            print('please pass a url to load command')
            return

        if rt.srcurl != '': rt.free()

        url = arg
        if url != '':
            if rt.load(url) is None:
                print('Fail to load file: ', url)
            else:
                print('Successfully loaded file ', url)
                self.brief('')

    def free(self, arg:str):
        '''
        Breif:  Release a rtmv file
        Usage:  free
        Option: None
        '''
        rt = self.rt
        rt.free()
        print('Successfully free the rtmv file: ', rt.srcurl)

    def dump(self, arg: str):
        '''
        Brief: Dump data from the current rtmv file.
        Usage: dump -o url [--option=OPTION] [-p pkg_scope]
        Options:
            -o url     specify the output file or folder (while the option is set as images)
            --option=OPTION
                payload: dump payload only to the file
                header: dump headers as a cvs file
                pkg_all: dump the entire packages
                pkg_vid: dump video package(s) only
                pkg_pic: dump image pakcage(s) only
                payload_vid: dump video payload only
                payload_pic: dump image payload oonly
                route: dump flight route to a geojson file  
            -p 0-100
                the index of start & end pakcages you want to dump. all packages count if it is not set.
        Examples:
            dump -o testfile.rtmv --option=pkg_vid # dump all video package to the file testfile.rtmv
            dump -o test.h264 --option=payload_vid # dump all video payload to the fine test.h264
            dump -o images --option=payload_pic # dump all image payload to the folder images including a pos file
            dump -o headers.csv --option=header -p 0-1000 # dump headers to headers.csv file from package 0 to 1000
        '''
        rt = self.rt
        if (rt is None) | (rt.srcurl == ''):
            print('Please load a rtmv file first.')
            return
        url = ''
        pkgs = ()
        option = ''
        args = getopt.getopt(arg.split(' '), '-o:-p:', ['option='])[0]
        for opt, val in args:
            if opt == '-o':
                url = val
                continue
            if opt == '-p': 
                pkgs = range(int(val.split('-')[0]), int(val.split('-')[1])+1)
                continue
            if opt == '--option':
                option = val
                continue

        if url == '':
            print('please input the url for the command dump')
        elif option == '':
            print('please select an option for the command dump')
        else:
            rt.dump(url, option, pkgs)

    def header(self, arg: str):
        '''
        Brief:      Print the headers specified (index starting from 0).
        Usage:      header 100 # print the header of the 100th package (starting from 0)
                    header 0-10 # print the headers of packages from 0 to 10 inclusive
                    header 0,1,5 # print the headers of the package 0, 1, 5
        Option:     to be defined
        '''
        rt = self.rt
        if arg.isdigit(): 
            pkgs = (int(arg),)
        elif len(arg.split('-')) == 2: 
            pkgs = range(int(arg.split('-')[0]), int(arg.split('-')[1]))
        else:
            #pkgs = list(map(int, arg.split(',')))
            pkgs = [int(x) for x in arg.split(',')]
        
        if rt.srcurl != '':
            if pkgs[-1] >= len(rt.rtmvpackages):
                print("the required package doesn't exit.")
            else:
                for i in pkgs:
                    print('Header info of the package {0}{1}:'.format(i, '-'*50+'>'))
                    for j in rt.protocol:
                        print('{0:<16}{1}'.format(j.name+':', rt.rtmvpackages[i][1][rt.protocol.index(j)]))
        else:
            print("Please load a rtmv file first.")

    def exit(self, arg: str): 
        '''
        Brief:      Quit the program.
        Usage:      exit
        Option:     None
        '''
        self.free('')
        sys.exit(0) # what the parameter 2 means here?
        pass

if __name__ == "__main__":
    
    print(sys.argv)

    all_cmd = [a for a in dir(RtmvParserCmd) if a[0]!= '_']
    all_cmd.sort()
    if len(sys.argv) > 1:
        rt = RtmvParser(sys.argv[1])
    else:
        rt = RtmvParser()
    rt_cmd = RtmvParserCmd(rt)

    print(all_cmd)

    while True:
        cmdline = input('rtmv>')
        cmd = cmdline.strip().split(' ', 1)
        arg = ''
        if len(cmd) > 1: 
            arg = cmd[1].strip()

        if cmd[0] in all_cmd: getattr(rt_cmd, cmd[0])(arg)
        elif cmd[0] == 'help':
            if arg in all_cmd: 
                print(getattr(rt_cmd, arg).__doc__)
            else:
                print('The following command is support, type help [command] for details.')
                for c in all_cmd:
                    print('{:<16}{}'.format(c+':', getattr(rt_cmd, c).__doc__.split('\n',3)[1].strip().split(' ',1)[1].strip()))
        else:
            os.system(cmdline) # pass to the system (dir or ls)
#            print('command is not supported, please type "help" for help')
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   rtmv_gui.py
@Time    :   2021/02/06 21:17:18
@Author  :   Zhengwei GUAN @ SIBITU
@Contact :   zhengwei.guan@hotmail.com; zhengwei.guan@insmapper.com
@Desc    :   GUI for rtmv parsing
'''

import sys, os, time, threading, io
import json
from collections import namedtuple
from enum import Enum

from PySide6.QtCore import SIGNAL, QObject
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTreeWidget, QTreeWidgetItem, QLabel, QPushButton
from PySide6.QtWidgets import QHeaderView, QStackedLayout
from PySide6.QtGui import QImage, QPixmap
from rtmv_main import Ui_MainWindow
from rtmvfile import RtmvParser, RtmvPayloadSection
from rtmv_labelplayer import RtmvVideoPlayer

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pkgViewerDock.setWindowTitle('RTMV Package Viwer')
        self.ui.actionOpen_O.triggered.connect(self.loadRtmv)
        self.ui.actionClose_C.triggered.connect(self.freeRtmv)

        self.rt = None

        # this is for section labels to indicate different paylaod section.
        # one section means a series of continuous packages with same type of payload, i.e. video or pictures
        RtmvPayloadSection = namedtuple('RtmvPayloadSection', ['pos', 'end', 'type', 'content'])
        self.sectionlabels = []
        self.sectiontree = []
        self.payload_sections = []

        self.section_tree_layout = QStackedLayout(self.ui.section_tree_widget)
        self.section_tree_layout.setStackingMode(QStackedLayout.StackingMode.StackOne)
        self.section_tree_layout.setObjectName(u"section_tree_layout")
        self.section_tree_layout.setContentsMargins(2, 2, 2, 2)

        # init the payload media player
        self.ui.pb_player_playpause.clicked.connect(self._playerPlayPause)
        self.ui.pb_player_stop.clicked.connect(self._playerStop)

        # Set up player event handling
        self.ui.label_player.sectionLoadStatusChanged.connect(self._onPlayerLoadedStatusChange)
        self.ui.label_player.playerPlayingStatusChanged.connect(self._onPlayerPlayingStatusChnange)
        self.ui.label_player.playingProgressChanged.connect(self._onplayingProgressChange)

    # several overall status of the app
    # 1. rtmv loading status
    # 2. player status

    def _onplayingProgressChange(self, cur_time):
        val = int(cur_time)
        if val != self.ui.horizontalSlider.value():
            self.ui.horizontalSlider.setValue(val)
            self.ui.label_player_curtime.setText(f'{int(val//60):>02}:{val%60:>02}')

    def _onPlayerPlayingStatusChnange(self, stat):
        # Mainly alter the status of playpause button and stop button
        if stat == RtmvVideoPlayer.State.STOPPED:
            self.ui.pb_player_playpause.setText("▶")
            self.ui.pb_player_stop.setEnabled(False)
            self.ui.horizontalSlider.setValue(0)
            self.ui.label_player_curtime.setText('00:00')
        elif stat == RtmvVideoPlayer.State.PAUSE:
            self.ui.pb_player_playpause.setText("▶")
        elif stat == RtmvVideoPlayer.State.PLAYING:
            self.ui.pb_player_playpause.setText("⏸")
            self.ui.pb_player_stop.setEnabled(True)
        else:
            logger.warning(f'Wrong player status "{stat}"')

    def _onPlayerLoadedStatusChange(self, ps: RtmvPayloadSection):
        if ps is not None:
            # Newly loaded a payload section
            # * Enable play/stop button
            # * Enable and set time indicators
            # * Enable slider bar (or pgorgress bar)
            # * Anything else?
            self.ui.pb_player_playpause.setEnabled(True)
            self.ui.pb_player_stop.setEnabled(False)

            self.ui.label_player_curtime.setEnabled(True)
            self.ui.label_player_curtime.setText('00:00')
            m, s = divmod(ps.duration, 60)  # Get minutes & seconds
            self.ui.label_player_duration.setText(f'{int(m):>02}:{int(s):>02}')
            self.ui.label_player_duration.setEnabled(True)
            self.ui.horizontalSlider.setMaximum(int(ps.duration))

            self.ui.horizontalSlider.setEnabled(True)
        else:
            self.ui.pb_player_playpause.setEnabled(False)
            self.ui.pb_player_stop.setEnabled(False)
            self.ui.label_player_curtime.setText('00:00')
            self.ui.label_player_curtime.setEnabled(False)
            self.ui.label_player_duration.setText('00:00')
            self.ui.label_player_duration.setEnabled(False)
            self.ui.horizontalSlider.setEnabled(True)

    def _playerPlayPause(self):
        if self.rt is None: return
        if len(self.payload_sections) < 1: return

        if self.ui.label_player.stat == RtmvVideoPlayer.State.STOPPED:
            # prepare the parameters
            self.ui.label_player.play(self.payload_sections[0])

        elif self.ui.label_player.stat == RtmvVideoPlayer.State.PAUSE:
            self.ui.label_player.resume()

        elif self.ui.label_player.stat == RtmvVideoPlayer.State.PLAYING:
            self.ui.label_player.pause()

        else:
            logger.warning(f'Wrong player status')

    def _playerStop(self):
        if self.rt is None: return
        if self.ui.label_player.stat != RtmvVideoPlayer.State.STOPPED:
            self.ui.label_player.stop()

    def loadRtmv(self):
        # Load file
        furl, _ = QFileDialog.getOpenFileName(self,"Open a RTMV File", os.path.abspath('.'),"RTMV Files (*.rtmv);; ALL Files (*)")
        if furl == '': return
        if self.rt is not None:
            self.freeRtmv()

        # Load the rtmv file
        self.rt = RtmvParser(furl)
        if self.rt is None:
            print(f'Fail to load the file {furl}.')
            return

        # get the payload sections of the rtmv
        self.payload_sections = self.rt.payload_sections

        # Set up package tree
        top_item = QTreeWidgetItem()
        top_item.setText(0, os.path.split(self.rt.srcurl)[1])
        self.ui.pkgTreeWidget.addTopLevelItem(top_item)
        for i, pkg in enumerate(self.rt.rtmvpackages):
            # generate the package tree
            pkg_item = QTreeWidgetItem(top_item, [f'{"timestamp:":<16}{pkg[1].timestamp}'])
            pkg_item.setText(0, f'package {i:0>5}: {"video" if pkg[1].vid_codec == 4 else "Pic"} {pkg[0],pkg[2]}')
            # insert the child items timestamp, gps, Height, cam p/y/r, payload type
            QTreeWidgetItem(pkg_item, [f'{"timestamp:":<16}{pkg[1].timestamp}'])
            QTreeWidgetItem(pkg_item, [f'{"gps:":<16}{pkg[1].lat}, {pkg[1].long}, {pkg[1].alt}'])
            QTreeWidgetItem(pkg_item, [f'{"height:":<16}{pkg[1].height}'])
            QTreeWidgetItem(pkg_item, [f'{"cam pyr:":<16}{pkg[1].cam_pitch}, {pkg[1].cam_yaw}, {pkg[1].cam_roll}'])
        top_item.setExpanded(True)

        # set the label UI
        for i, ps in enumerate(self.payload_sections):
            label_txt = f'{ps.type.name} {self.rt.getDuration(ps.start, ps.end):.2f}s'
            self.sectionlabels.append(QPushButton(label_txt, self.ui.section_labels_widget)) # create section label
            self.sectionlabels[-1].setObjectName(f'section_label_{i}')
            self.sectionlabels[-1].setToolTipDuration(-1)
            self.sectionlabels[-1].setCheckable(True)
            self.sectionlabels[-1].setChecked(False)
            self.sectionlabels[-1].clicked.connect(self.sectionLabelClicked)

            self.ui.pkg_bar_hlayout.addWidget(self.sectionlabels[-1])
            self.ui.pkg_bar_hlayout.setStretch(i, round(self.rt.getDuration(ps.start, ps.end)))

            # add the section view tree
            self.sectiontree.append(QTreeWidget(self.ui.section_tree_widget))
            self.sectiontree[-1].setObjectName(f'Section Tree {i}')
            self.sectiontree[-1].header().setVisible(True)
            self.sectiontree[-1].setColumnCount(2)
            self.sectiontree[-1].setHeaderLabels(['Key', 'Value'])
            self.sectiontree[-1].header().setSectionResizeMode(QHeaderView.ResizeToContents)

            # set up the payload section tree with section content
            self.sectiontree[-1].clear()
            top = QTreeWidgetItem()
            top.setText(0, f'{os.path.split(self.rt.srcurl)[1]} Payload Section {i:>02}:')
            self.sectiontree[-1].addTopLevelItem(top)
            self._loadJsonTree(self.sectiontree[-1], ps.meta, top)
            self.section_tree_layout.addWidget(self.sectiontree[-1])

        if len(self.payload_sections) > 0:
            # TODO: show the payload content
            self._current_sec = 0
            self.sectionlabels[self._current_sec].setChecked(True)
            self.section_tree_layout.setCurrentIndex(self._current_sec)

            # Load player
            if self.payload_sections[self._current_sec].type == RtmvParser.PayloadType.VIDEO:
                self.ui.label_player.loadSection(self.payload_sections[self._current_sec])

    def _loadJsonTree(self, tree:QTreeWidget, js, tree_item): # generate all items according to the tree.
        if type(js) == list:
            tree_item.setExpanded(True)
            for i,v in enumerate(js):
                item = QTreeWidgetItem(tree_item, [f'Item {i:>05}:'])
                self._loadJsonTree(self, v, item)
        elif type(js) == dict:
            tree_item.setExpanded(True)
            for k, v in js.items():
                if (type(v) is list) or (type(v) is dict):
                    item = QTreeWidgetItem(tree_item, [f'{k} ({len(v)}):'])
                    self._loadJsonTree(self, v, item)
                else:
                    item = QTreeWidgetItem(tree_item, [f'{k}', f'{v}'])
        else:
            item = QTreeWidgetItem(tree_item, [f'{js}']) # is this necessory?

    def sectionLabelClicked(self):
        # set checked status first
        label_clicked = self.sender()
        if label_clicked is not self.sectionlabels[self._current_sec]:
            for i,label in enumerate(self.sectionlabels):
                if label is label_clicked:
                    label.setChecked(True)
                    self._current_sec = i
                else:
                    label.setChecked(False)

            # Update the section information
            self.section_tree_layout.setCurrentIndex(self._current_sec)

    def sectionInfoUpdate(self, label):
        pass

    def freeRtmv(self):
        # free the section player
        self.ui.label_player.freeSection()

        # clear package tree
        self.ui.pkgTreeWidget.clear()

        # clear the package viewer
        for i, v in enumerate(self.sectionlabels):
            self.ui.pkg_bar_hlayout.removeWidget(v)
            v.deleteLater()
            self.section_tree_layout.removeWidget(self.sectiontree[i])
            self.sectiontree[i].deleteLater()

        self.sectionlabels.clear()
        self.sectiontree.clear()
        self.payload_sections.clear()

        # release rtmv
        if self.rt is not None:
            self.rt.free()
            self.rt = None

    def clear(self):
        self.freeRtmv()

        if self.rt is not None:
            self.rt.free()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.aboutToQuit.connect(window.clear)
    sys.exit(app.exec_())

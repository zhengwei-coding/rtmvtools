# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rtmv_main.ui'
##
## Created by: Qt User Interface Compiler version 6.0.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from rtmv_labelplayer import RtmvVideoPlayer


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(994, 639)
        self.actionOpen_O = QAction(MainWindow)
        self.actionOpen_O.setObjectName(u"actionOpen_O")
        self.actionClose_C = QAction(MainWindow)
        self.actionClose_C.setObjectName(u"actionClose_C")
        self.actionExit_E = QAction(MainWindow)
        self.actionExit_E.setObjectName(u"actionExit_E")
        self.actionExport_Packages = QAction(MainWindow)
        self.actionExport_Packages.setObjectName(u"actionExport_Packages")
        self.actionExport_Payload = QAction(MainWindow)
        self.actionExport_Payload.setObjectName(u"actionExport_Payload")
        self.actionExport_Headers = QAction(MainWindow)
        self.actionExport_Headers.setObjectName(u"actionExport_Headers")
        self.actionHelp_H = QAction(MainWindow)
        self.actionHelp_H.setObjectName(u"actionHelp_H")
        self.actionAbout_A = QAction(MainWindow)
        self.actionAbout_A.setObjectName(u"actionAbout_A")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pkgContantTabWidget = QTabWidget(self.centralwidget)
        self.pkgContantTabWidget.setObjectName(u"pkgContantTabWidget")
        self.pkgContantTabWidget.setAutoFillBackground(False)
        self.payload_viewer = QWidget()
        self.payload_viewer.setObjectName(u"payload_viewer")
        self.verticalLayout_2 = QVBoxLayout(self.payload_viewer)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(9, 9, 9, 0)
        self.section_labels_widget = QWidget(self.payload_viewer)
        self.section_labels_widget.setObjectName(u"section_labels_widget")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.section_labels_widget.sizePolicy().hasHeightForWidth())
        self.section_labels_widget.setSizePolicy(sizePolicy)
        self.section_labels_widget.setMinimumSize(QSize(80, 20))
        self.pkg_bar_hlayout = QHBoxLayout(self.section_labels_widget)
        self.pkg_bar_hlayout.setSpacing(0)
        self.pkg_bar_hlayout.setObjectName(u"pkg_bar_hlayout")
        self.pkg_bar_hlayout.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_2.addWidget(self.section_labels_widget)

        self.section_tree_widget = QWidget(self.payload_viewer)
        self.section_tree_widget.setObjectName(u"section_tree_widget")

        self.verticalLayout_2.addWidget(self.section_tree_widget)

        self.pkgContantTabWidget.addTab(self.payload_viewer, "")
        self.media_viewer = QWidget()
        self.media_viewer.setObjectName(u"media_viewer")
        self.verticalLayout_3 = QVBoxLayout(self.media_viewer)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 9)
        self.label_player = RtmvVideoPlayer(self.media_viewer)
        self.label_player.setObjectName(u"label_player")
        self.label_player.setFrameShape(QFrame.StyledPanel)
        self.label_player.setScaledContents(False)
        self.label_player.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_player)

        self.wdgt_playerctrl = QWidget(self.media_viewer)
        self.wdgt_playerctrl.setObjectName(u"wdgt_playerctrl")
        sizePolicy.setHeightForWidth(self.wdgt_playerctrl.sizePolicy().hasHeightForWidth())
        self.wdgt_playerctrl.setSizePolicy(sizePolicy)
        self.horizontalLayout_4 = QHBoxLayout(self.wdgt_playerctrl)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.pb_player_playpause = QPushButton(self.wdgt_playerctrl)
        self.pb_player_playpause.setObjectName(u"pb_player_playpause")
        self.pb_player_playpause.setEnabled(False)
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pb_player_playpause.sizePolicy().hasHeightForWidth())
        self.pb_player_playpause.setSizePolicy(sizePolicy1)
        self.pb_player_playpause.setMinimumSize(QSize(24, 24))
        self.pb_player_playpause.setMaximumSize(QSize(24, 24))

        self.gridLayout.addWidget(self.pb_player_playpause, 1, 1, 1, 1)

        self.pb_player_next = QPushButton(self.wdgt_playerctrl)
        self.pb_player_next.setObjectName(u"pb_player_next")
        self.pb_player_next.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pb_player_next.sizePolicy().hasHeightForWidth())
        self.pb_player_next.setSizePolicy(sizePolicy1)
        self.pb_player_next.setMinimumSize(QSize(24, 24))
        self.pb_player_next.setMaximumSize(QSize(24, 24))

        self.gridLayout.addWidget(self.pb_player_next, 1, 3, 1, 1)

        self.pb_player_pre = QPushButton(self.wdgt_playerctrl)
        self.pb_player_pre.setObjectName(u"pb_player_pre")
        self.pb_player_pre.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pb_player_pre.sizePolicy().hasHeightForWidth())
        self.pb_player_pre.setSizePolicy(sizePolicy1)
        self.pb_player_pre.setMinimumSize(QSize(24, 24))
        self.pb_player_pre.setMaximumSize(QSize(24, 24))

        self.gridLayout.addWidget(self.pb_player_pre, 1, 0, 1, 1)

        self.pb_player_stop = QPushButton(self.wdgt_playerctrl)
        self.pb_player_stop.setObjectName(u"pb_player_stop")
        self.pb_player_stop.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.pb_player_stop.sizePolicy().hasHeightForWidth())
        self.pb_player_stop.setSizePolicy(sizePolicy1)
        self.pb_player_stop.setMinimumSize(QSize(24, 24))
        self.pb_player_stop.setMaximumSize(QSize(24, 24))

        self.gridLayout.addWidget(self.pb_player_stop, 1, 2, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 0, 0, 1, 1)


        self.horizontalLayout_4.addLayout(self.gridLayout)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_player_curtime = QLabel(self.wdgt_playerctrl)
        self.label_player_curtime.setObjectName(u"label_player_curtime")
        self.label_player_curtime.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.label_player_curtime)

        self.horizontalSpacer = QSpacerItem(398, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.label_player_duration = QLabel(self.wdgt_playerctrl)
        self.label_player_duration.setObjectName(u"label_player_duration")
        self.label_player_duration.setEnabled(False)
        self.label_player_duration.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.label_player_duration)

        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 4)
        self.horizontalLayout_3.setStretch(2, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalSlider = QSlider(self.wdgt_playerctrl)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setEnabled(False)
        self.horizontalSlider.setOrientation(Qt.Horizontal)

        self.verticalLayout.addWidget(self.horizontalSlider)

        self.verticalLayout.setStretch(0, 1)

        self.horizontalLayout_4.addLayout(self.verticalLayout)


        self.verticalLayout_3.addWidget(self.wdgt_playerctrl)

        self.pkgContantTabWidget.addTab(self.media_viewer, "")

        self.horizontalLayout.addWidget(self.pkgContantTabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 994, 22))
        self.menuFile_F = QMenu(self.menubar)
        self.menuFile_F.setObjectName(u"menuFile_F")
        self.menuExport = QMenu(self.menubar)
        self.menuExport.setObjectName(u"menuExport")
        self.menuHelp_H = QMenu(self.menubar)
        self.menuHelp_H.setObjectName(u"menuHelp_H")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.pkgViewerDock = QDockWidget(MainWindow)
        self.pkgViewerDock.setObjectName(u"pkgViewerDock")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.pkgViewerDock.sizePolicy().hasHeightForWidth())
        self.pkgViewerDock.setSizePolicy(sizePolicy2)
        self.pkgViewerDock.setMinimumSize(QSize(200, 113))
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.horizontalLayout_2 = QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.pkgTreeWidget = QTreeWidget(self.dockWidgetContents)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.pkgTreeWidget.setHeaderItem(__qtreewidgetitem)
        self.pkgTreeWidget.setObjectName(u"pkgTreeWidget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.pkgTreeWidget.sizePolicy().hasHeightForWidth())
        self.pkgTreeWidget.setSizePolicy(sizePolicy3)
        font = QFont()
        font.setPointSize(9)
        self.pkgTreeWidget.setFont(font)
        self.pkgTreeWidget.header().setVisible(False)

        self.horizontalLayout_2.addWidget(self.pkgTreeWidget)

        self.pkgViewerDock.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.pkgViewerDock)

        self.menubar.addAction(self.menuFile_F.menuAction())
        self.menubar.addAction(self.menuExport.menuAction())
        self.menubar.addAction(self.menuHelp_H.menuAction())
        self.menuFile_F.addAction(self.actionOpen_O)
        self.menuFile_F.addAction(self.actionClose_C)
        self.menuFile_F.addSeparator()
        self.menuFile_F.addAction(self.actionExit_E)
        self.menuExport.addAction(self.actionExport_Packages)
        self.menuExport.addAction(self.actionExport_Payload)
        self.menuExport.addAction(self.actionExport_Headers)
        self.menuHelp_H.addAction(self.actionHelp_H)
        self.menuHelp_H.addAction(self.actionAbout_A)

        self.retranslateUi(MainWindow)

        self.pkgContantTabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionOpen_O.setText(QCoreApplication.translate("MainWindow", u"Open (&O)", None))
        self.actionClose_C.setText(QCoreApplication.translate("MainWindow", u"Close (C)", None))
        self.actionExit_E.setText(QCoreApplication.translate("MainWindow", u"Exit (&E)", None))
        self.actionExport_Packages.setText(QCoreApplication.translate("MainWindow", u"Export Packages...", None))
        self.actionExport_Payload.setText(QCoreApplication.translate("MainWindow", u"Export Payload...", None))
        self.actionExport_Headers.setText(QCoreApplication.translate("MainWindow", u"Export Headers...", None))
        self.actionHelp_H.setText(QCoreApplication.translate("MainWindow", u"Help (&H)", None))
        self.actionAbout_A.setText(QCoreApplication.translate("MainWindow", u"About (A)", None))
        self.pkgContantTabWidget.setTabText(self.pkgContantTabWidget.indexOf(self.payload_viewer), QCoreApplication.translate("MainWindow", u"Payload Overview", None))
        self.label_player.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.pb_player_playpause.setText(QCoreApplication.translate("MainWindow", u"\u25b6", None))
        self.pb_player_next.setText(QCoreApplication.translate("MainWindow", u"\u23ed", None))
        self.pb_player_pre.setText(QCoreApplication.translate("MainWindow", u"\u23ee", None))
        self.pb_player_stop.setText(QCoreApplication.translate("MainWindow", u"\u25a0", None))
        self.label_player_curtime.setText(QCoreApplication.translate("MainWindow", u"00:00", None))
        self.label_player_duration.setText(QCoreApplication.translate("MainWindow", u"00:00", None))
        self.pkgContantTabWidget.setTabText(self.pkgContantTabWidget.indexOf(self.media_viewer), QCoreApplication.translate("MainWindow", u"Media Player", None))
        self.menuFile_F.setTitle(QCoreApplication.translate("MainWindow", u"File (&F)", None))
        self.menuExport.setTitle(QCoreApplication.translate("MainWindow", u"Export (&E)", None))
        self.menuHelp_H.setTitle(QCoreApplication.translate("MainWindow", u"Help (&H)", None))
    # retranslateUi


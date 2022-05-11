# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_win2.ui'
##
## Created by: Qt User Interface Compiler version 6.0.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1050, 621)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.playButton = QPushButton(self.centralwidget)
        self.playButton.setObjectName(u"playButton")
        self.playButton.setGeometry(QRect(350, 540, 51, 24))
        self.treeWidgetHeaders = QTreeWidget(self.centralwidget)
        font = QFont()
        font.setBold(True)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setTextAlignment(0, Qt.AlignCenter);
        __qtreewidgetitem.setFont(0, font);
        self.treeWidgetHeaders.setHeaderItem(__qtreewidgetitem)
        self.treeWidgetHeaders.setObjectName(u"treeWidgetHeaders")
        self.treeWidgetHeaders.setGeometry(QRect(10, 30, 321, 541))
        self.treeWidgetHeaders.setAcceptDrops(True)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 131, 16))
        self.frame_payload = QFrame(self.centralwidget)
        self.frame_payload.setObjectName(u"frame_payload")
        self.frame_payload.setGeometry(QRect(350, 30, 691, 461))
        self.frame_payload.setAutoFillBackground(True)
        self.frame_payload.setFrameShape(QFrame.StyledPanel)
        self.frame_payload.setFrameShadow(QFrame.Raised)
        self.label_vid = QLabel(self.frame_payload)
        self.label_vid.setObjectName(u"label_vid")
        self.label_vid.setGeometry(QRect(10, 10, 661, 441))
        self.label_osd = QLabel(self.frame_payload)
        self.label_osd.setObjectName(u"label_osd")
        self.label_osd.setGeometry(QRect(10, 10, 391, 121))
        font1 = QFont()
        font1.setFamily(u"Nirmala UI Semilight")
        font1.setPointSize(16)
        font1.setBold(True)
        self.label_osd.setFont(font1)
        self.label_osd.setAutoFillBackground(False)
        self.horizontalSlider = QSlider(self.centralwidget)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setGeometry(QRect(420, 543, 621, 18))
        self.horizontalSlider.setOrientation(Qt.Horizontal)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1050, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
#if QT_CONFIG(tooltip)
        self.actionOpen.setToolTip(QCoreApplication.translate("MainWindow", u"Open", None))
#endif // QT_CONFIG(tooltip)
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.playButton.setText(QCoreApplication.translate("MainWindow", u"Play", None))
        ___qtreewidgetitem = self.treeWidgetHeaders.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"All Packages", None));
        self.label.setText(QCoreApplication.translate("MainWindow", u"Package Headers", None))
        self.label_vid.setText("")
        self.label_osd.setText(QCoreApplication.translate("MainWindow", u"This is a test~~~~", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
    # retranslateUi


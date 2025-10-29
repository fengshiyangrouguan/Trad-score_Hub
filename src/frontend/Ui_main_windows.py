# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_windows.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
    QPlainTextEdit, QPushButton, QSizePolicy, QSpacerItem,
    QSplitter, QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1024, 673)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.widget_image = QWidget(self.splitter)
        self.widget_image.setObjectName(u"widget_image")
        self.verticalLayout = QVBoxLayout(self.widget_image)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.layout_vbox_image = QVBoxLayout()
        self.layout_vbox_image.setObjectName(u"layout_vbox_image")
        self.label_image = QLabel(self.widget_image)
        self.label_image.setObjectName(u"label_image")

        self.layout_vbox_image.addWidget(self.label_image)

        self.widget = QWidget(self.widget_image)
        self.widget.setObjectName(u"widget")
        self.widget.setMaximumSize(QSize(16777215, 70))
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.btn_next = QPushButton(self.widget)
        self.btn_next.setObjectName(u"btn_next")
        self.btn_next.setMinimumSize(QSize(0, 40))
        self.btn_next.setMaximumSize(QSize(70, 40))

        self.horizontalLayout.addWidget(self.btn_next)

        self.btn_prev = QPushButton(self.widget)
        self.btn_prev.setObjectName(u"btn_prev")
        self.btn_prev.setMaximumSize(QSize(70, 40))

        self.horizontalLayout.addWidget(self.btn_prev)


        self.layout_vbox_image.addWidget(self.widget)


        self.verticalLayout.addLayout(self.layout_vbox_image)

        self.label = QLabel(self.widget_image)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(16777215, 25))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.splitter.addWidget(self.widget_image)
        self.widget_2 = QWidget(self.splitter)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout_2 = QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.text_input = QPlainTextEdit(self.widget_2)
        self.text_input.setObjectName(u"text_input")

        self.verticalLayout_2.addWidget(self.text_input)

        self.btn_generate = QPushButton(self.widget_2)
        self.btn_generate.setObjectName(u"btn_generate")
        self.btn_generate.setMinimumSize(QSize(0, 40))
        self.btn_generate.setMaximumSize(QSize(16777215, 40))

        self.verticalLayout_2.addWidget(self.btn_generate)

        self.btn_input = QPushButton(self.widget_2)
        self.btn_input.setObjectName(u"btn_input")
        self.btn_input.setMinimumSize(QSize(0, 40))
        self.btn_input.setMaximumSize(QSize(16777215, 40))

        self.verticalLayout_2.addWidget(self.btn_input)

        self.btn_save = QPushButton(self.widget_2)
        self.btn_save.setObjectName(u"btn_save")
        self.btn_save.setMinimumSize(QSize(0, 40))
        self.btn_save.setMaximumSize(QSize(16777215, 40))

        self.verticalLayout_2.addWidget(self.btn_save)

        self.splitter.addWidget(self.widget_2)

        self.horizontalLayout_2.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_image.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.btn_next.setText(QCoreApplication.translate("MainWindow", u"\u2190", None))
        self.btn_prev.setText(QCoreApplication.translate("MainWindow", u"\u2192", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\uff08\u4e50\u8c31\u56fe\u7247\u6587\u4ef6\u4fdd\u5b58\u5728data/scores_img/\u4e2d\uff09", None))
        self.btn_generate.setText(QCoreApplication.translate("MainWindow", u"\u751f\u6210\u4e50\u8c31", None))
        self.btn_input.setText(QCoreApplication.translate("MainWindow", u"\u5bfc\u5165\u6570\u5b57\u5316\u4e50\u8c31", None))
        self.btn_save.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58\u4e50\u8c31", None))
    # retranslateUi


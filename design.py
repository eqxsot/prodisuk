# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'control_panel.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(571, 397)
        MainWindow.setMinimumSize(QtCore.QSize(571, 397))
        MainWindow.setMaximumSize(QtCore.QSize(571, 397))
        MainWindow.setWindowTitle("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowOpacity(1.0)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(10, 30, 411, 261))
        self.listWidget.setObjectName("listWidget")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(10, 300, 411, 25))
        self.textEdit.setObjectName("textEdit")
        self.send_message_button = QtWidgets.QPushButton(self.centralwidget)
        self.send_message_button.setGeometry(QtCore.QRect(430, 300, 131, 25))
        self.send_message_button.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.send_message_button.setObjectName("send_message_button")
        self.add_admin_button = QtWidgets.QPushButton(self.centralwidget)
        self.add_admin_button.setGeometry(QtCore.QRect(150, 330, 131, 25))
        self.add_admin_button.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.add_admin_button.setObjectName("add_admin_button")
        self.add_user_button = QtWidgets.QPushButton(self.centralwidget)
        self.add_user_button.setGeometry(QtCore.QRect(10, 330, 131, 25))
        self.add_user_button.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.add_user_button.setObjectName("add_user_button")
        self.change_name_button = QtWidgets.QPushButton(self.centralwidget)
        self.change_name_button.setGeometry(QtCore.QRect(290, 330, 131, 25))
        self.change_name_button.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.change_name_button.setObjectName("change_name_button")
        self.users = QtWidgets.QListWidget(self.centralwidget)
        self.users.setGeometry(QtCore.QRect(430, 160, 131, 131))
        self.users.setObjectName("users")
        self.admins = QtWidgets.QListWidget(self.centralwidget)
        self.admins.setGeometry(QtCore.QRect(430, 30, 131, 111))
        self.admins.setObjectName("admins")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(430, 10, 111, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(430, 140, 121, 20))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(450, 330, 91, 21))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(10, 10, 47, 13))
        self.label_4.setObjectName("label_4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 571, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.send_message_button.setText(_translate("MainWindow", "Отправить"))
        self.add_admin_button.setText(_translate("MainWindow", "Добавить админа"))
        self.add_user_button.setText(_translate("MainWindow", "Добавить пользователя"))
        self.change_name_button.setText(_translate("MainWindow", "Изменить имя сессии"))
        self.label.setText(_translate("MainWindow", "Администраторы:"))
        self.label_2.setText(_translate("MainWindow", "Пользователи:"))
        self.label_3.setText(_translate("MainWindow", "by __eqx__, 2021"))
        self.label_4.setText(_translate("MainWindow", "Консоль:"))

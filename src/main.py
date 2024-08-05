# coding: utf-8 

"""
Embeddium - Vector Embedding Generation Application

This module contains the main window implementation for the Embeddium application.

Author: Anish Reddy
Version: 1.0.0
Date: August 4, 2024
License: [TBD]

Usage:
    Run this script to launch the Embeddium application.
"""

import sys
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QApplication

from qfluentwidgets import * #FIX
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow

from ui.titlebar import CustomTitleBar
from ui.stacked_widget import StackedWidget

from scripts.file_input import FileInputWidget
from scripts.model_selection import ModelSelectionWidget
from scripts.output_options import OutputOptionsWidget
from scripts.generate_embeddings import GenerateEmbeddingsWidget
from scripts.settings import SettingsWidget

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    if os.path.basename(base_path) == 'src':
        base_path = os.path.dirname(base_path)

    return os.path.join(base_path, relative_path)

class Window(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))

        setTheme(Theme.DARK)
        setThemeColor('#9b63d9')

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationBar = NavigationBar(self)
        self.stackWidget = StackedWidget(self)

        # Create interfaces
        self.fileInputInterface = FileInputWidget(self)
        self.modelSelectionInterface = ModelSelectionWidget(self)
        self.outputOptionsInterface = OutputOptionsWidget(self)
        self.generateEmbeddingsInterface = GenerateEmbeddingsWidget(self)
        self.settingsInterface = SettingsWidget(self)

        self.initLayout()
        self.initNavigation()
        self.initWindow()

        self.fileInputInterface.fileSelected.connect(self.updateFileInfo)
        self.modelSelectionInterface.modelSelected.connect(self.updateModelInfo)
        self.outputOptionsInterface.outputConfigured.connect(self.updateOutputInfo)

        self.updateModelInfo(self.modelSelectionInterface.selected_model)

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 48, 0, 0)
        self.hBoxLayout.addWidget(self.navigationBar)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.fileInputInterface, FIF.FOLDER, 'File Input')
        self.addSubInterface(self.modelSelectionInterface, FIF.IOT, 'Select Model')
        self.addSubInterface(self.outputOptionsInterface, FIF.SAVE, 'Output')
        self.addSubInterface(self.generateEmbeddingsInterface, FIF.PLAY, 'Embed')
        self.addSubInterface(self.settingsInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)
        
        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.navigationBar.setCurrentItem(self.fileInputInterface.objectName())

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationBar.setCurrentItem(widget.objectName())

        if widget == self.generateEmbeddingsInterface:
            self.updateEmbeddingInfo()

    def updateFileInfo(self, file_path, filename):
        self.generateEmbeddingsInterface.updateInfo(inputFile=file_path)

    def updateModelInfo(self, model_name):
        self.generateEmbeddingsInterface.updateInfo(model=model_name)

    def updateOutputInfo(self, output_format, output_location):
        self.generateEmbeddingsInterface.updateInfo(
            outputFormat=output_format,
            outputLocation=output_location
        )

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def initWindow(self):
        self.resize(900, 700)

        icon_path = resource_path('resources/icons/logo.ico')
        
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle('Embeddium')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        self.setQss()

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP):
        self.stackWidget.addWidget(interface)
        self.navigationBar.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
        )

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        qss_file = resource_path(os.path.join('resources', 'resource', color, 'demo.qss'))
        try:
            with open(qss_file, encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"QSS file not found: {qss_file}")

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationBar.setCurrentItem(widget.objectName())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()
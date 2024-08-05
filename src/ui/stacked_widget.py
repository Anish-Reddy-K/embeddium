from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QFrame

from qfluentwidgets import PopUpAniStackedWidget

class StackedWidget(QFrame):
    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.view = PopUpAniStackedWidget(self)


        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.view)

        self.view.currentChanged.connect(self.currentChanged)

    def addWidget(self, widget):
        self.view.addWidget(widget)

    def widget(self, index: int):
        return self.view.widget(index)

    def setCurrentWidget(self, widget, popOut=False):
        self.view.setCurrentWidget(widget, duration=0)

    def setCurrentIndex(self, index, popOut=False):
        self.view.setCurrentIndex(index)
        self.setCurrentWidget(self.view.widget(index), popOut)
import os
import shutil
import pandas as pd
import chardet
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class FileDragDropWidget(QWidget):
    fileDropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Drag & Drop File Here\nor Click to Select")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                background-color: #2a2a2a;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.label)
        
        self.supported_formats = ['.csv', '.json', '.txt', '.xlsx']

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if os.path.splitext(file_path)[1].lower() in self.supported_formats:
                event.acceptProposedAction()
                self.label.setStyleSheet("""
                    QLabel {
                        border: 2px solid #0078d4;
                        border-radius: 5px;
                        padding: 20px;
                        background-color: #1e1e1e;
                        font-size: 12px;
                    }
                """)
            else:
                event.ignore()

    def dragLeaveEvent(self, event):
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                background-color: #2a2a2a;
                font-size: 12px;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.process_file(file_path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            file_dialog = QFileDialog()
            file_dialog.setNameFilter("Supported Files (*.csv *.json *.txt *.xlsx)")
            file_path, _ = file_dialog.getOpenFileName(self, "Select File", "", "Supported Files (*.csv *.json *.txt *.xlsx)")
            if file_path:
                self.process_file(file_path)

    def process_file(self, file_path):
        self.copy_file(file_path)
        self.fileDropped.emit(file_path)

    def copy_file(self, file_path):
        upload_dir = "uploaded_files"
        os.makedirs(upload_dir, exist_ok=True)
        filename = os.path.basename(file_path)
        destination = os.path.join(upload_dir, filename)
        try:
            shutil.copy2(file_path, destination)
            print(f"File saved to: {destination}")
        except Exception as e:
            print(f"Error saving file: {str(e)}")

    def enterEvent(self, event):
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                background-color: #1e1e1e;
                font-size: 12px;
            }
        """)

    def leaveEvent(self, event):
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                background-color: #2a2a2a;
                font-size: 12px;
            }
        """)
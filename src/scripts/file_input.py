import os
import shutil

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from qfluentwidgets import *

from scripts.file_drag_drop import FileDragDropWidget

class FileInputWidget(QWidget):
    fileSelected = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.selected_file = None
        layout = QVBoxLayout(self)
        
        titleLabel = TitleLabel("Input your data File")
        layout.addWidget(titleLabel)

        subLabel = CaptionLabel("Accepted file formats: .csv, .json, .txt, .xlsx")
        layout.addWidget(subLabel)

        self.fileWidget = FileDragDropWidget(self)
        self.fileWidget.fileDropped.connect(self.handle_file_selection)
        layout.addWidget(self.fileWidget)

        self.uploadedFileLabel = SubtitleLabel("No file uploaded")
        layout.addWidget(self.uploadedFileLabel)
        
        layout.addStretch(1)
        
        self.setObjectName("FileInput")

        # Create a directory to store uploaded files
        self.upload_dir = os.path.join(os.getcwd(), "uploaded_files")
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def show_upload_success(self, filename):
        InfoBar.success(
            title='File Uploaded',
            content=f"'{filename}' has been uploaded successfully",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=3000,
            parent=self
        )    

    def handle_file_selection(self, file_path):
        self.selected_file = file_path
        filename = os.path.basename(file_path)
        self.fileSelected.emit(file_path, filename)

        # Copy the file to the upload directory
        destination = os.path.join(self.upload_dir, filename)
        try:
            shutil.copy2(file_path, destination)
            print(f"File saved to: {destination}")
            self.show_upload_success(filename)
            self.uploadedFileLabel.setText(f"Uploaded file: {filename}")
            
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            
            # Show error notification
            InfoBar.error(
                title='Upload Failed',
                content=f"Failed to upload '{filename}': {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,
                parent=self
            )
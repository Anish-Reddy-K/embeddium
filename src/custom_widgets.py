import os
import shutil
import pandas as pd
import chardet
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class FileDragDropWidget(QWidget):
    fileDropped = pyqtSignal(str, str)

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
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.csv':
            self.preview_csv(file_path)
        elif file_extension == '.json':
            self.preview_json(file_path)
        elif file_extension == '.xlsx':
            self.preview_xlsx(file_path)
        elif file_extension == '.txt':
            self.preview_txt(file_path)
        
        # Copy the file to the upload directory
        self.copy_file(file_path)

    def copy_file(self, file_path):
        # Create a directory to store uploaded files if it doesn't exist
        upload_dir = "uploaded_files"
        os.makedirs(upload_dir, exist_ok=True)
        filename = os.path.basename(file_path)
        destination = os.path.join(upload_dir, filename)
        try:
            # shutil.copy2(file_path, destination)
            # print(f"File saved to: {destination}")
            pass
        except Exception as e:
            # print(f"Error saving file: {str(e)}")
            pass

    def preview_csv(self, file_path):
        try:
            # Detect file encoding
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
            encoding = result['encoding']
            
            # Read the CSV file
            df = pd.read_csv(file_path, encoding=encoding)
            
            # Get total number of rows and columns
            total_rows, total_cols = df.shape
            
            # Limit the preview to the first 5 rows and 10 columns
            df_preview = df.iloc[:5, :10]
            
            # Convert DataFrame to string representation
            preview_content = df_preview.to_string(index=False)
            
            # Add messages about truncation
            preview_content += f"\n\nPreview shows {min(5, total_rows)} rows out of {total_rows} total rows."
            if total_cols > 10:
                preview_content += f"\nShowing only the first 10 columns out of {total_cols} total columns."

            self.fileDropped.emit(file_path, preview_content)
        except Exception as e:
            self.fileDropped.emit(file_path, f"Error reading CSV file: {str(e)}")

    def preview_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Convert the JSON data to a formatted string
            formatted_json = json.dumps(data, indent=2)
            
            # Limit the preview to the first 1000 characters
            preview_content = formatted_json[:1000]
            
            # Add message about truncation
            if len(formatted_json) > 1000:
                preview_content += "\n...\n"
                preview_content += f"Preview truncated. Showing 1000 out of {len(formatted_json)} characters."
            else:
                preview_content += f"\n\nShowing all {len(formatted_json)} characters of the JSON file."

            self.fileDropped.emit(file_path, preview_content)
        except Exception as e:
            self.fileDropped.emit(file_path, f"Error reading JSON file: {str(e)}")
    
    def preview_xlsx(self, file_path):
        try:
            # Read the Excel file
            df = pd.read_excel(file_path)
            
            # Get the total number of rows and columns
            total_rows = len(df)
            total_cols = len(df.columns)
            
            # Limit the preview to the first 5 rows and 10 columns
            df_preview = df.iloc[:5, :10]
            
            # Convert DataFrame to string representation
            preview_content = df_preview.to_string(index=False)
            
            # Add messages about truncation
            preview_content += f"\n\nPreview shows {min(5, total_rows)} rows out of {total_rows} total rows."
            
            if total_cols > 10:
                preview_content += f"\nShowing only the first 10 columns out of {total_cols} total columns."

            self.fileDropped.emit(file_path, preview_content)
        except Exception as e:
            self.fileDropped.emit(file_path, f"Error reading Excel file: {str(e)}")

    def preview_txt(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Limit the preview to the first 1000 characters
            preview_content = content[:1000]
            
            # Add message about truncation
            if len(content) > 1000:
                preview_content += "\n...\n"
                preview_content += f"Preview truncated. Showing 1000 out of {len(content)} characters."
            else:
                preview_content += f"\n\nShowing all {len(content)} characters of the text file."

            self.fileDropped.emit(file_path, preview_content)
        except Exception as e:
            self.fileDropped.emit(file_path, f"Error reading text file: {str(e)}")

    def enterEvent(self, event):
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                background-color: #1e1e1e;  /* Change background color on hover */
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

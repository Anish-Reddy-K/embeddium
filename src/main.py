# coding: utf-8 

import sys
import os
import platform
import shutil

from PyQt5.QtCore import Qt, pyqtSignal, QEasingCurve, QUrl, QTimer, QThread
from PyQt5.QtGui import QIcon, QDesktopServices,QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QApplication, QFrame, QWidget, QTextEdit, QFileDialog, QComboBox, QProgressBar, QGridLayout

from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, TitleBar

from custom_widgets import FileDragDropWidget
from embedding_backend import EmbeddingBackend

import torch

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    if os.path.basename(base_path) == 'src':
        base_path = os.path.dirname(base_path)

    return os.path.join(base_path, relative_path)

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

class ModelSelectionWidget(QWidget):
    modelSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.selected_model = None
        self.initUI()

        default_model = "all-MiniLM-L6-v2"
        #self.updateModelInfo(default_model)
    
    def setDefaultModel(self, model_name):
        self.selected_model = model_name
        self.updateModelInfo(model_name, emit_signal=False)

    def initUI(self):
        layout = QVBoxLayout(self)
        
        titleLabel = TitleLabel("Select Embedding Model")
        layout.addWidget(titleLabel)

        subtitleLabel = BodyLabel("List of the most popular models from sentence-transformers")
        layout.addWidget(subtitleLabel)

        self.modelDropdown = DropDownPushButton(FluentIcon.IOT, 'Select Model')
        self.createModelMenu()
        layout.addWidget(self.modelDropdown)

        self.modelInfoCard = CardWidget(self)
        cardLayout = QVBoxLayout(self.modelInfoCard)
        
        # Stats layout
        self.statsLayout = QHBoxLayout()
        self.modelSizeBadge = InfoBadge.custom('', '#FF4500', '#37ab56')  # Bright orange with white text
        self.sentenceEmbeddingBadge = InfoBadge.custom('', '#005fb8', '#60cdff')
        self.semanticSearchBadge = InfoBadge.custom('', '#00a86b', '#60cdff')
        self.avgPerformanceBadge = InfoBadge.custom('', '#d65db1', '#60cdff')
        self.speedBadge = InfoBadge.custom('', '#ff8c00', '#60cdff')

        self.statsLayout.addWidget(QLabel("Model Size:"))
        self.statsLayout.addWidget(self.modelSizeBadge)
        self.statsLayout.addWidget(QLabel("Sentence Embeddings:"))
        self.statsLayout.addWidget(self.sentenceEmbeddingBadge)
        self.statsLayout.addWidget(QLabel("Semantic Search:"))
        self.statsLayout.addWidget(self.semanticSearchBadge)
        self.statsLayout.addWidget(QLabel("Avg. Performance:"))
        self.statsLayout.addWidget(self.avgPerformanceBadge)
        self.statsLayout.addWidget(QLabel("Speed:"))
        self.statsLayout.addWidget(self.speedBadge)
        
        cardLayout.addLayout(self.statsLayout)
        
        # Description
        self.modelDescriptionEdit = TextEdit()
        self.modelDescriptionEdit.setReadOnly(True)
        self.modelDescriptionEdit.setTextInteractionFlags(Qt.NoTextInteraction)  # Disable text selection
        self.modelDescriptionEdit.setPlaceholderText("Model description will appear here")
        cardLayout.addWidget(self.modelDescriptionEdit)
        
        layout.addWidget(self.modelInfoCard)

        layout.addStretch(1)
        self.setObjectName("ModelSelection")

        # Set default model
        self.updateModelInfo("all-MiniLM-L6-v2")

    def createModelMenu(self):
        menu = RoundMenu(parent=self.modelDropdown)
        models = [
            "all-mpnet-base-v2",
            "multi-qa-mpnet-base-dot-v1",
            "all-distilroberta-v1",
            "all-MiniLM-L12-v2",
            "multi-qa-distilbert-cos-v1",
            "all-MiniLM-L6-v2",
            "multi-qa-MiniLM-L6-cos-v1",
            "paraphrase-multilingual-mpnet-base-v2",
            "paraphrase-albert-small-v2",
            "paraphrase-multilingual-MiniLM-L12-v2",
            "paraphrase-MiniLM-L3-v2",
            "distiluse-base-multilingual-cased-v1",
            "distiluse-base-multilingual-cased-v2"
        ]

        for model_name in models:
            action = Action(FluentIcon.IOT, model_name)
            action.triggered.connect(lambda checked, m=model_name: self.updateModelInfo(m))
            menu.addAction(action)

        self.modelDropdown.setMenu(menu)

    def updateModelInfo(self, model_name, emit_signal=True):
        self.selected_model = model_name
        self.modelSelected.emit(model_name)

        self.modelDropdown.setText(model_name)
        
        # Use InfoBar to display the model name in the top right corner
        InfoBar.success(
            title='Selected Model',
            content=model_name,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT, 
            duration=3000,
            parent=self
        )
        
        model_data = {
            "all-mpnet-base-v2": ["69.57", "57.02", "63.30", "2800", "420 MB"],
            "multi-qa-mpnet-base-dot-v1": ["66.76", "57.60", "62.18", "2800", "420 MB"],
            "all-distilroberta-v1": ["68.73", "50.94", "59.84", "4000", "290 MB"],
            "all-MiniLM-L12-v2": ["68.70", "50.82", "59.76", "7500", "120 MB"],
            "multi-qa-distilbert-cos-v1": ["65.98", "52.83", "59.41", "4000", "250 MB"],
            "all-MiniLM-L6-v2": ["68.06", "49.54", "58.80", "14200", "80 MB"],
            "multi-qa-MiniLM-L6-cos-v1": ["64.33", "51.83", "58.08", "14200", "80 MB"],
            "paraphrase-multilingual-mpnet-base-v2": ["65.83", "41.68", "53.75", "2500", "970 MB"],
            "paraphrase-albert-small-v2": ["64.46", "40.04", "52.25", "5000", "43 MB"],
            "paraphrase-multilingual-MiniLM-L12-v2": ["64.25", "39.19", "51.72", "7500", "420 MB"],
            "paraphrase-MiniLM-L3-v2": ["62.29", "39.19", "50.74", "19000", "61 MB"],
            "distiluse-base-multilingual-cased-v1": ["61.30", "29.87", "45.59", "4000", "480 MB"],
            "distiluse-base-multilingual-cased-v2": ["60.18", "27.35", "43.77", "4000", "480 MB"]
        }

        if model_name in model_data:
            data = model_data[model_name]
            self.modelSizeBadge.setText(data[4])
            self.sentenceEmbeddingBadge.setText(data[0])
            self.semanticSearchBadge.setText(data[1])
            self.avgPerformanceBadge.setText(data[2])
            self.speedBadge.setText(data[3])
        
        description = (
            "This model is part of the sentence-transformers collection. "
            "It has been trained on a large and diverse dataset to provide high-quality sentence embeddings. "
            "The model can be used for various natural language processing tasks such as semantic similarity, "
            "clustering, and information retrieval."
        )
        self.modelDescriptionEdit.setPlainText(description)

        if emit_signal:
            self.modelSelected.emit(model_name)

class OutputOptionsWidget(QWidget):
    outputConfigured = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.selected_format = None
        self.selected_location = None

        self.initUI()
        self.formatCombo.currentIndexChanged.connect(self.update_format)

        self.selected_format = self.formatCombo.currentText()
        self.outputConfigured.emit(self.selected_format, "")

    def initUI(self):
        layout = QVBoxLayout(self)
        
        titleLabel = TitleLabel("Output Configuration")
        layout.addWidget(titleLabel)

        subtitleLabel = BodyLabel("Select output format and location")
        layout.addWidget(subtitleLabel)

        # Output format selection
        formatCard = CardWidget(self)
        formatLayout = QVBoxLayout(formatCard)
        formatLabel = BodyLabel("Select Output Format:")
        self.formatCombo = ComboBox()
        self.formatCombo.addItems([".pt", ".npy", ".hdf5", ".faiss"])
        formatLayout.addWidget(formatLabel)
        formatLayout.addWidget(self.formatCombo)
        layout.addWidget(formatCard)

        # Save location
        locationCard = CardWidget(self)
        locationLayout = QVBoxLayout(locationCard)
        locationLabel = BodyLabel("Output Location:")
        self.locationDisplay = LineEdit()
        self.locationDisplay.setReadOnly(True)
        self.locationDisplay.setPlaceholderText("No location selected")

        self.selectLocationBtn = PushButton("Select Location", icon=FluentIcon.FOLDER)
        self.selectLocationBtn.clicked.connect(self.select_output_location)
        locationLayout.addWidget(locationLabel)
        locationLayout.addWidget(self.locationDisplay)
        locationLayout.addWidget(self.selectLocationBtn)
        layout.addWidget(locationCard)

        layout.addStretch(1)
        self.setObjectName("OutputOptions")

    def select_output_location(self):
        folder_dialog = QFileDialog()
        folder_path = folder_dialog.getExistingDirectory(self, "Select Output Location")
        if folder_path:
            self.locationDisplay.setText(folder_path)
            self.selected_location = folder_path
            self.outputConfigured.emit(self.selected_format, folder_path)

            self.locationDisplay.setText(folder_path)
            InfoBar.success(
                title='Location Selected',
                content=f"Output location set to: {folder_path}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
    
    def update_format(self, index):
        self.selected_format = self.formatCombo.currentText().lstrip('.')  
        self.outputConfigured.emit(self.selected_format, self.selected_location or "")

class EmbeddingWorker(QThread):
    progress_updated = pyqtSignal(dict)
    embedding_completed = pyqtSignal(str, dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, backend, input_file, output_dir, model, output_name, output_format, batch_size):
        super().__init__()
        self.backend = backend
        self.input_file = input_file
        self.output_dir = output_dir
        self.model = model
        self.output_name = output_name
        self.output_format = output_format
        self.batch_size = batch_size

    def run(self):
        try:
            # Connect signals
            self.backend.progress_updated.connect(self.progress_updated.emit)
            self.backend.embedding_completed.connect(self.embedding_completed.emit)
            self.backend.error_occurred.connect(self.error_occurred.emit)
            
            self.backend.embed_file(self.input_file, self.output_dir, self.model, self.output_name, self.output_format, self.batch_size)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            # Disconnect signals safely
            try:
                self.backend.progress_updated.disconnect(self.progress_updated.emit)
            except TypeError:
                pass
            try:
                self.backend.embedding_completed.disconnect(self.embedding_completed.emit)
            except TypeError:
                pass
            try:
                self.backend.error_occurred.disconnect(self.error_occurred.emit)
            except TypeError:
                pass

class GenerateEmbeddingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initUI()
        self.backend = EmbeddingBackend()
        self.worker = None
        self.embedding_in_progress = False
        self.embedding_completed = False

        # self.backend.progress_updated.connect(self.updateProgress)
        # self.backend.embedding_completed.connect(self.embeddingCompleted)
        # self.backend.error_occurred.connect(self.showError)

    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Info Card
        infoCard = CardWidget(self)
        infoLayout = QGridLayout(infoCard)
        
        infoLayout.addWidget(StrongBodyLabel("Input File:"), 0, 0)
        self.inputFileLabel = BodyLabel("No file selected")
        infoLayout.addWidget(self.inputFileLabel, 0, 1)
        
        infoLayout.addWidget(StrongBodyLabel("Model:"), 1, 0)
        self.modelLabel = BodyLabel("No model selected")
        infoLayout.addWidget(self.modelLabel, 1, 1)
        
        infoLayout.addWidget(StrongBodyLabel("Output Format:"), 2, 0)
        self.outputFormatLabel = BodyLabel("Not specified")
        infoLayout.addWidget(self.outputFormatLabel, 2, 1)
        
        infoLayout.addWidget(StrongBodyLabel("Output Location:"), 3, 0)
        self.outputLocationLabel = BodyLabel("Not specified")
        infoLayout.addWidget(self.outputLocationLabel, 3, 1)
        
        layout.addWidget(infoCard)
        
        # # Buttons
        # buttonLayout = QHBoxLayout()
        # self.startButton = PushButton("Start Embedding")
        # self.startButton.setEnabled(True)
        # self.startButton.clicked.connect(self.checkAndStartEmbedding)

        # self.cancelButton = PushButton("Cancel Embedding")
        # self.cancelButton.setEnabled(False)
        # buttonLayout.addWidget(self.startButton)
        # buttonLayout.addWidget(self.cancelButton)
        # layout.addLayout(buttonLayout)
        # self.cancelButton.clicked.connect(self.cancelEmbedding)

        # Progress Card
        progressCard = CardWidget(self)
        progressLayout = QVBoxLayout(progressCard)

        # Progress Bar
        self.progressBar = ProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        progressLayout.addWidget(BodyLabel("Embedding Progress:"))
        progressLayout.addWidget(self.progressBar)

        # Estimated Time Remaining
        self.timeRemainingLabel = BodyLabel("Estimated Time Remaining: --:--")
        progressLayout.addWidget(self.timeRemainingLabel)

        # Speed
        self.speedLabel = BodyLabel("Processing Speed: -- items/s")
        progressLayout.addWidget(self.speedLabel)

        # Memory Usage
        self.memoryLabel = BodyLabel("Memory Usage: -- MB")
        progressLayout.addWidget(self.memoryLabel)

        # Error Count
        self.errorLabel = BodyLabel("Errors: 0")
        progressLayout.addWidget(self.errorLabel)

        # Add new labels for additional post-embedding statistics
        self.dimensionLabel = BodyLabel("Embedding Dimension: --")
        progressLayout.addWidget(self.dimensionLabel)

        self.modelNameLabel = BodyLabel("Model Used: --")
        progressLayout.addWidget(self.modelNameLabel)

        self.outputSizeLabel = BodyLabel("Output Size: -- MB")
        progressLayout.addWidget(self.outputSizeLabel)
        
        layout.addWidget(progressCard)

        # Progress Ring
        self.progressRing = ProgressRing()
        self.progressRing.setFixedSize(80, 80)
        self.progressRing.setTextVisible(True)
        self.progressRing.setRange(0, 100)
        self.progressRing.setValue(0)

        layout.addWidget(self.progressRing, alignment=Qt.AlignCenter)

        # self.embeddingSaveInfoLabel = BodyLabel("")
        # self.embeddingSaveInfoLabel.hide()
        # layout.addWidget(self.embeddingSaveInfoLabel)

        self.outputInfoLabel = BodyLabel("")
        layout.addWidget(self.outputInfoLabel)

        # Buttons
        buttonLayout = QHBoxLayout()
        self.startButton = PushButton("Start Embedding")
        self.startButton.clicked.connect(self.startEmbedding)
        self.cancelButton = PushButton("Cancel Embedding")
        self.cancelButton.setEnabled(False)
        self.cancelButton.clicked.connect(self.cancelEmbedding)
        buttonLayout.addWidget(self.startButton)
        buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonLayout)
        # Connect buttons to methods

        self.setObjectName("GenerateEmbeddings")

    def updateInfo(self, inputFile=None, model=None, outputFormat=None, outputLocation=None):
        if inputFile is not None:
            self.inputFileLabel.setText(inputFile)
        if model is not None:
            self.modelLabel.setText(model)
        if outputFormat is not None:
            self.outputFormatLabel.setText(outputFormat if outputFormat else "Not specified")
        if outputLocation is not None:
            self.outputLocationLabel.setText(outputLocation if outputLocation else "Not specified")

    def checkAndStartEmbedding(self):
        missing_params = self.getMissingParams()
        if missing_params:
            self.showMissingParamsTeachingTip(missing_params)
        else:
            self.startEmbedding()

    def getMissingParams(self):
        missing_params = []
        if self.inputFileLabel.text() in ["", "No file selected"]:
            missing_params.append("Input File")
        if self.modelLabel.text() in ["", "No model selected"]:
            missing_params.append("Model")
        if self.outputFormatLabel.text() in ["", "Not specified"]:
            missing_params.append("Output Format")
        if self.outputLocationLabel.text() in ["", "Not specified"]:
            missing_params.append("Output Location")
        return missing_params

    def showMissingParamsTeachingTip(self, missing_params):
        missing_str = ", ".join(missing_params)
        content = f"Please set the following before starting:\n{missing_str}"
        
        TeachingTip.create(
            target=self.startButton,
            icon=InfoBarIcon.WARNING,
            title='Missing Parameters',
            content=content,
            isClosable=True,
            tailPosition=TeachingTipTailPosition.TOP,
            duration=3000,
            parent=self
        )

    def startEmbedding(self):
        # Only start if all parameters are set
        # Get parameters from other widgets
        input_file = self.inputFileLabel.text()
        model = self.modelLabel.text()
        output_format = self.outputFormatLabel.text().lstrip('.')
        output_location = self.outputLocationLabel.text()
        output_name = "embeddings"  # You can make this configurable if needed
        batch_size = 32  # You can make this configurable if needed

        if not os.path.isabs(input_file):
            input_file = os.path.join(os.getcwd(), "uploaded_files", input_file)

        self.worker = EmbeddingWorker(self.backend, input_file, output_location, model, output_name, output_format, batch_size)

        self.worker.progress_updated.connect(self.updateProgress)
        self.worker.embedding_completed.connect(self.embeddingCompleted)
        self.worker.error_occurred.connect(self.showError)
        self.worker.finished.connect(self.workerFinished)
        self.worker.start()

        self.embedding_in_progress = True
        self.embedding_completed = False
        self.startButton.setEnabled(False)
        self.cancelButton.setEnabled(True)
        # if not self.getMissingParams():
        #     self.startButton.setEnabled(False)
        #     self.cancelButton.setEnabled(True)
        #     self.progressBar.setValue(0)
        #     self.progressRing.setValue(0)
            
        #     # Start the timer to simulate progress
        #     self.timer.start(500)  # Update every 0.5 seconds
        # else:
        #     # This shouldn't happen normally, but just in case
        #     self.showMissingParamsTeachingTip(self.getMissingParams())
       
        
    def cancelEmbedding(self):
        if self.worker and self.worker.isRunning():
            self.backend.cancel_embedding()
            self.worker.wait()
        self.embedding_completed = False
        self.resetUI()

    def resetUI(self):
        if not self.embedding_completed:
            self.progressBar.setValue(0)
            self.progressRing.setValue(0)
            self.timeRemainingLabel.setText("Estimated Time Remaining: --:--")
            self.speedLabel.setText("Processing Speed: -- items/s")
            self.memoryLabel.setText("Memory Usage: -- MB")
            self.errorLabel.setText("Errors: 0")
            self.outputInfoLabel.setText("")
            self.dimensionLabel.setText("Embedding Dimension: --")
            self.modelNameLabel.setText("Model Used: --")
            self.outputSizeLabel.setText("Output Size: -- MB")
        
        self.startButton.setEnabled(True)
        self.cancelButton.setEnabled(False)
        self.embedding_in_progress = False

    def workerFinished(self):
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
        if not self.embedding_completed:
            self.resetUI()
    # def cancelEmbedding(self):
    #     # This method would be called when the cancel button is clicked
    #     self.timer.stop()  # Stop the timer
    #     self.startButton.setEnabled(True)
    #     self.cancelButton.setEnabled(False)
    #     self.progressBar.setValue(0)
    #     self.progressRing.setValue(0)
    #     self.timeRemainingLabel.setText("Estimated Time Remaining: --:--")

        # # Show error flyout
        # InfoBar.error(
        #     title='Embedding Cancelled',
        #     content="The embedding process was cancelled.",
        #     orient=Qt.Horizontal,
        #     isClosable=True,
        #     position=InfoBarPosition.TOP_RIGHT,
        #     duration=3000,
        #     parent=self
        # )

    def updateProgress(self, stats):
        self.progressBar.setValue(int(stats["progress"]))
        self.progressRing.setValue(int(stats["progress"]))
        self.timeRemainingLabel.setText(f"Estimated Time Remaining: {stats['eta']:.2f}s")
        self.speedLabel.setText(f"Processing Speed: {stats['speed']:.2f} items/s")
        self.memoryLabel.setText(f"Memory Usage: {stats['memory_usage']:.2f} MB")
        self.errorLabel.setText(f"Errors: {stats['error_count']}")

    # def updateProgress(self):
    #     # This method simulates progress updates (replace with actual logic)
    #     currentValue = self.progressBar.value()
    #     if currentValue < 100:
    #         newValue = currentValue + 5
    #         self.progressBar.setValue(newValue)
    #         self.progressRing.setValue(newValue)
            
    #         # Update time remaining (this is a placeholder calculation)
    #         remainingTime = (100 - newValue) * 0.5  # 0.5 seconds per 1% progress
    #         minutes, seconds = divmod(int(remainingTime), 60)
    #         self.timeRemainingLabel.setText(f"Estimated Time Remaining: {minutes:02d}:{seconds:02d}")
    #     else:
    #         self.timer.stop()
    #         self.startButton.setEnabled(True)
    #         self.cancelButton.setEnabled(False)
    #         self.timeRemainingLabel.setText("Embedding Complete!")

    #         filename = self.inputFileLabel.text()
    #         location = self.outputLocationLabel.text()
    #         self.embeddingSaveInfoLabel.setText(f"Embedding 'embeddings' saved in: {location}")
    #         self.embeddingSaveInfoLabel.show() 
    #         self.show_embedding_success(filename, location)
    
    def embeddingCompleted(self, output_file, stats):
        self.embedding_in_progress = False
        self.embedding_completed = True
        
        # Update labels with post-embedding statistics
        self.timeRemainingLabel.setText(f"Total Time: {stats['total_time']:.2f} seconds")
        self.speedLabel.setText(f"Average Speed: {stats['speed']:.2f} items/s")
        self.memoryLabel.setText(f"Peak Memory Usage: {stats['memory_usage']:.2f} MB")
        self.errorLabel.setText(f"Total Errors: {stats['error_count']}")
        
        # Add new labels for additional post-embedding statistics
        self.outputInfoLabel.setText(f"Output File: {output_file}")
        self.dimensionLabel.setText(f"Embedding Dimension: {stats['embedding_dim']}")
        self.modelNameLabel.setText(f"Model Used: {stats['model_name']}")
        self.outputSizeLabel.setText(f"Output Size: {stats['output_size']:.2f} MB")
        
        self.startButton.setEnabled(True)
        self.cancelButton.setEnabled(False)

        InfoBar.success(
            title='Embedding Complete',
            content=f"Embedding saved to: {output_file}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=5000,
            parent=self
        )

    def showError(self, error_message):
        if not self.embedding_completed:
            self.resetUI()
        
        InfoBar.error(
            title='Embedding Error',
            content=error_message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=5000,
            parent=self
        )

    def show_embedding_success(self, filename, location):
        InfoBar.success(
            title='Embedding Complete',
            content=f"Embedding for '{filename}' has been saved in: {location}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=5000,
            parent=self
        )

class SettingsWidget(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Computation Device Settings")
        self.setBorderRadius(8)
        self.setContentsMargins(0, 0, 0, 16)  # Add bottom margin

        self.initUI()

    def initUI(self):
        # Device Type Selection
        self.deviceTypeCombo = ComboBox()
        self.deviceTypeCombo.addItems(["CPU", "GPU"])
        self.deviceTypeCombo.setFixedWidth(200)
        self.deviceTypeCombo.currentIndexChanged.connect(self.updateDeviceList)

        self.addGroup(
            FluentIcon.IOT, 
            "Computation Device",
            "Choose between CPU and GPU for computations",
            self.deviceTypeCombo
        )

        # Specific Device Selection
        self.deviceListCombo = ComboBox()
        self.deviceListCombo.setFixedWidth(200)

        self.addGroup(
            FluentIcon.IOT,
            "Specific Device",
            "Select a specific device for computation",
            self.deviceListCombo
        )

        self.vBoxLayout.addSpacing(40)
        self.addPersonalInfoSection() 

        # Apply Button
        self.applyButton = PushButton("Apply Settings")
        self.applyButton.clicked.connect(self.applySettings)
        self.applyButton.setFixedHeight(40)
        
        # Create a container widget for the button with padding
        buttonContainer = QWidget()
        buttonLayout = QHBoxLayout(buttonContainer)
        buttonLayout.setContentsMargins(16, 0, 16, 0)  # Add horizontal padding
        buttonLayout.addWidget(self.applyButton)
        
        # Add the button container to the layout
        self.vBoxLayout.addStretch()
        self.vBoxLayout.addWidget(buttonContainer)

        self.updateDeviceList()

    def updateDeviceList(self):
        self.deviceListCombo.clear()
        if self.deviceTypeCombo.currentText() == "CPU":
            cpu_name = platform.processor()
            self.deviceListCombo.addItem(f"CPU: {cpu_name}")
        else:
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    self.deviceListCombo.addItem(f"GPU {i}: {torch.cuda.get_device_name(i)}")
            else:
                self.deviceListCombo.addItem("No GPU available")

    def applySettings(self):
        deviceType = self.deviceTypeCombo.currentText()
        specificDevice = self.deviceListCombo.currentText()
        
        settingsInfo = f"Device: {deviceType} - {specificDevice}"
        
        InfoBar.success(
            title='Settings Applied',
            content=settingsInfo,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=5000,
            parent=self
        )

    def addPersonalInfoSection(self):
        personalInfoCard = CardWidget(self)
        layout = QVBoxLayout(personalInfoCard)

        titleLabel = StrongBodyLabel("Developer Information")
        layout.addWidget(titleLabel)

        nameButton = HyperlinkButton(FluentIcon.CONNECT, "https://yourportfolio.com", "Your Name")
        
        githubButton = HyperlinkButton(FluentIcon.GITHUB, "https://github.com/yourusername", "GitHub: yourusername")
        
        websiteButton = HyperlinkButton(FluentIcon.LINK, "https://yourwebsite.com", "Personal Website")
        
        emailButton = HyperlinkButton(FluentIcon.MAIL , "mailto:your.email@example.com", "Email")

        appWebsiteButton = HyperlinkButton(FluentIcon.GLOBE, "https://embeddium.app", "App Website: Embeddium")

        layout.addWidget(nameButton)
        layout.addWidget(githubButton)
        layout.addWidget(websiteButton)
        layout.addWidget(emailButton)
        layout.addWidget(appWebsiteButton)

        self.vBoxLayout.addWidget(personalInfoCard)

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

class CustomTitleBar(TitleBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.hBoxLayout.removeWidget(self.minBtn)
        self.hBoxLayout.removeWidget(self.maxBtn)
        self.hBoxLayout.removeWidget(self.closeBtn)

        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 20)
        self.hBoxLayout.insertWidget(
            1, self.iconLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.window().windowIconChanged.connect(self.setIcon)

        self.titleLabel = QLabel(self)
        self.hBoxLayout.insertWidget(
            2, self.titleLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.titleLabel.setObjectName('titleLabel')
        self.window().windowTitleChanged.connect(self.setTitle)

        self.vBoxLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(0)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setAlignment(Qt.AlignTop)
        self.buttonLayout.addWidget(self.minBtn)
        self.buttonLayout.addWidget(self.maxBtn)
        self.buttonLayout.addWidget(self.closeBtn)
        self.vBoxLayout.addLayout(self.buttonLayout)
        self.vBoxLayout.addStretch(1)
        self.hBoxLayout.addLayout(self.vBoxLayout, 0)

    def setTitle(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(18, 18))

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

        # Update the GenerateEmbeddingsWidget when switching to it
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

        # Update the GenerateEmbeddingsWidget when switching to it
        # if widget == self.generateEmbeddingsInterface:
        #     self.updateEmbeddingInfo()

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
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QGridLayout

from qfluentwidgets import CardWidget, StrongBodyLabel, BodyLabel, ProgressBar, ProgressRing, PushButton,TeachingTip, InfoBarIcon, TeachingTipTailPosition, InfoBar, InfoBarPosition

from backend.embedding import EmbeddingBackend
from backend.embedding_worker import EmbeddingWorker

class GenerateEmbeddingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initUI()
        self.backend = EmbeddingBackend()
        self.worker = None
        self.embedding_in_progress = False
        self.embedding_completed = False

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

    def updateProgress(self, stats):
        self.progressBar.setValue(int(stats["progress"]))
        self.progressRing.setValue(int(stats["progress"]))
        self.timeRemainingLabel.setText(f"Estimated Time Remaining: {stats['eta']:.2f}s")
        self.speedLabel.setText(f"Processing Speed: {stats['speed']:.2f} items/s")
        self.memoryLabel.setText(f"Memory Usage: {stats['memory_usage']:.2f} MB")
        self.errorLabel.setText(f"Errors: {stats['error_count']}")
    
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
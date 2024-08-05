# coding: utf-8 

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget

from qfluentwidgets import TitleLabel, BodyLabel, DropDownPushButton, CardWidget, FluentIcon, InfoBadge, TextEdit, RoundMenu, Action, InfoBar, InfoBarPosition

class ModelSelectionWidget(QWidget):
    modelSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.selected_model = None
        self.initUI()

        default_model = "all-MiniLM-L6-v2"
    
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
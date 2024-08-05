from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QFileDialog

from qfluentwidgets import TitleLabel, BodyLabel, CardWidget, ComboBox, LineEdit, PushButton, FluentIcon, InfoBar, InfoBarPosition

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
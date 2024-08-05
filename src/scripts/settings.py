import platform

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from qfluentwidgets import GroupHeaderCardWidget, ComboBox, FluentIcon, PushButton, InfoBar, InfoBarPosition, StrongBodyLabel, CardWidget, HyperlinkButton

import torch

class SettingsWidget(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Computation Device Settings")
        self.setBorderRadius(8)
        self.setContentsMargins(0, 0, 0, 16) 

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
import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QLabel, QFileDialog, QMessageBox
)
from utils import enhance_audio_file, enhance_video_file

class AudioEnhancerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Noise Remover and Voice Enhancer")
        self.setFixedSize(400, 200)

        self.layout = QVBoxLayout()
        self.label = QLabel("Select an audio or video file to enhance.")
        self.select_button = QPushButton("Select Video/Audio to Enhance")
        self.status_label = QLabel("Status: Idle")

        self.select_button.clicked.connect(self.process_file)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.select_button)
        self.layout.addWidget(self.status_label)
        self.setLayout(self.layout)

    def process_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Media Files (*.mp4 *.mov *.avi *.wav *.mp3)"
        )
        if not file_path:
            return

        self.label.setText(f"Selected: {os.path.basename(file_path)}")
        self.status_label.setText("Status: Processing...")
        QApplication.processEvents()

        try:
            ext = os.path.splitext(file_path)[1].lower()

            if ext in [".mp4", ".mov", ".avi"]:
                output_path = enhance_video_file(file_path)
            elif ext in [".wav", ".mp3"]:
                output_path = enhance_audio_file(file_path)
            else:
                raise ValueError("Unsupported file type selected.")

            self.status_label.setText(f"Status: Done!\nSaved to:\n{output_path}")
            QMessageBox.information(self, "Success", f"Enhanced file saved to:\n{output_path}")
        except Exception as e:
            self.status_label.setText("Status: Failed.")
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioEnhancerGUI()
    window.show()
    sys.exit(app.exec_())

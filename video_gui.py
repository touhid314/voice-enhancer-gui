import os
import sys
import tempfile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QLabel, QFileDialog, QMessageBox
)
from df.enhance import enhance, init_df, load_audio, save_audio
from moviepy.editor import VideoFileClip, AudioFileClip

class AudioEnhancerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Audio Enhancer (DeepFilterNet)")
        self.setFixedSize(500, 200)

        self.layout = QVBoxLayout()
        self.label = QLabel("Select a video file to enhance its audio.")
        self.select_button = QPushButton("Select Video")
        self.process_button = QPushButton("Enhance Audio")
        self.status_label = QLabel("Status: Idle")
        
        self.process_button.setEnabled(False)

        self.select_button.clicked.connect(self.select_video)
        self.process_button.clicked.connect(self.enhance_audio)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.select_button)
        self.layout.addWidget(self.process_button)
        self.layout.addWidget(self.status_label)

        self.setLayout(self.layout)
        self.video_path = None

        self.model, self.df_state, _ = init_df()

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File", "", "Video Files (*.mp4 *.mov *.avi)"
        )
        if file_path:
            self.video_path = file_path
            self.label.setText(f"Selected: {os.path.basename(file_path)}")
            self.process_button.setEnabled(True)

    def enhance_audio(self):
        if not self.video_path:
            QMessageBox.warning(self, "No Video Selected", "Please select a video file first.")
            return

        self.status_label.setText("Status: Enhancing audio... Please wait.")
        QApplication.processEvents()

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                raw_audio_path = os.path.join(tmpdir, "extracted_audio.wav")
                enhanced_audio_path = os.path.join(tmpdir, "enhanced_audio.wav")

                # Step 1: Extract audio
                video_clip = VideoFileClip(self.video_path)
                video_clip.audio.write_audiofile(raw_audio_path, fps=48000, codec='pcm_s16le')

                # Step 2: Load and enhance
                audio, _ = load_audio(raw_audio_path, sr=self.df_state.sr())
                enhanced_audio = enhance(self.model, self.df_state, audio)

                # Step 3: Save enhanced audio
                save_audio(enhanced_audio_path, enhanced_audio, self.df_state.sr())

                # Step 4: Replace audio in video
                base_name, ext = os.path.splitext(os.path.basename(self.video_path))
                output_video_path = os.path.join(os.path.dirname(self.video_path), f"{base_name}_ENHANCED{ext}")

                new_video = video_clip.set_audio(AudioFileClip(enhanced_audio_path))
                new_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")

            self.status_label.setText(f"Status: Done!\nSaved to:\n{output_video_path}")
            QMessageBox.information(self, "Success", f"Enhanced video saved to:\n{output_video_path}")
        except Exception as e:
            self.status_label.setText("Status: Failed.")
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioEnhancerGUI()
    window.show()
    sys.exit(app.exec_())

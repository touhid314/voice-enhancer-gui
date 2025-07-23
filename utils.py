"""
A voice enhancement utility using DeepFilterNet2(https://github.com/yuguochencuc/DeepFilterNet2).
Can enhance audio from both audio files and video files.
"""

import os
import tempfile
from df.enhance import enhance, init_df, load_audio, save_audio
from moviepy.editor import VideoFileClip, AudioFileClip

# Initialize DeepFilterNet only once
model, df_state, _ = init_df()

def enhance_audio_file(input_audio_path):
    """
    Enhances an audio file and saves the result as <name>_ENHANCED.wav in the same directory.
    """
    audio, _ = load_audio(input_audio_path, sr=df_state.sr())
    enhanced_audio = enhance(model, df_state, audio)

    base_name = os.path.splitext(os.path.basename(input_audio_path))[0]
    output_path = os.path.join(os.path.dirname(input_audio_path), f"{base_name}_ENHANCED_AUDIO.wav")
    save_audio(output_path, enhanced_audio, df_state.sr())
    return output_path

def enhance_video_file(input_video_path):
    """
    Extracts audio from a video, enhances it, and saves a new video with enhanced audio.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_audio_path = os.path.join(tmpdir, "extracted_audio.wav")
        enhanced_audio_path = os.path.join(tmpdir, "enhanced_audio.wav")

        # Extract audio
        video_clip = VideoFileClip(input_video_path)
        video_clip.audio.write_audiofile(raw_audio_path, fps=48000, codec='pcm_s16le')

        # Enhance audio
        audio, _ = load_audio(raw_audio_path, sr=df_state.sr())
        enhanced_audio = enhance(model, df_state, audio)
        save_audio(enhanced_audio_path, enhanced_audio, df_state.sr())

        # Replace audio in video
        base_name, ext = os.path.splitext(os.path.basename(input_video_path))
        output_video_path = os.path.join(os.path.dirname(input_video_path), f"{base_name}_ENHANCED_AUDIO{ext}")
        new_video = video_clip.set_audio(AudioFileClip(enhanced_audio_path))
        new_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")

    return output_video_path

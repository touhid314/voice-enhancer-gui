import os
from df.enhance import enhance, init_df, load_audio, save_audio
from moviepy.editor import VideoFileClip, AudioFileClip
import tempfile

def extract_audio_from_video(video_path, temp_audio_path):
    video_clip = VideoFileClip(video_path)
    audio = video_clip.audio
    audio.write_audiofile(temp_audio_path, fps=48000, codec='pcm_s16le')  # Save as WAV
    return temp_audio_path

def replace_audio_in_video(original_video_path, enhanced_audio_path, output_video_path):
    video_clip = VideoFileClip(original_video_path)
    enhanced_audio_clip = AudioFileClip(enhanced_audio_path)
    new_video = video_clip.set_audio(enhanced_audio_clip)
    new_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    video_path = r"C:\Users\TestUser\Downloads\Untitled video - Made with Clipchamp (1).mp4"

    # 1. Initialize DeepFilterNet
    model, df_state, _ = init_df()

    # 2. Extract audio from video
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_audio_path = os.path.join(tmpdir, "extracted_audio.wav")
        enhanced_audio_path = os.path.join(tmpdir, "enhanced_audio.wav")

        extract_audio_from_video(video_path, raw_audio_path)

        # 3. Load and enhance the audio
        audio, _ = load_audio(raw_audio_path, sr=df_state.sr())
        enhanced_audio = enhance(model, df_state, audio)

        # 4. Save the enhanced audio
        save_audio(enhanced_audio_path, enhanced_audio, df_state.sr())

        # 5. Replace audio in video
        base_name, ext = os.path.splitext(os.path.basename(video_path))
        output_video_path = f"{base_name}_ENHANCED_AUDIO{ext}"
        replace_audio_in_video(video_path, enhanced_audio_path, output_video_path)

        print(f"Enhanced video saved to: {output_video_path}")

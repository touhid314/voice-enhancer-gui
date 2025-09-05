"""
A voice enhancement utility using DeepFilterNet2(https://github.com/yuguochencuc/DeepFilterNet2).
Can enhance audio from both audio files and video files.
"""

import os
import tempfile
from df.enhance import enhance, init_df, load_audio, save_audio
from moviepy.editor import VideoFileClip, AudioFileClip
import soundfile as sf
import librosa
import numpy as np
import torch

# Initialize DeepFilterNet only once
# model, df_state, _ = init_df()

device = "cuda" if torch.cuda.is_available() else "cpu"
model, df_state, _ = init_df()
model = model.to(device)

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



CHUNK_DURATION_SEC = 5 * 60  # 5 minutes

def split_audio(input_audio_path, chunk_duration=CHUNK_DURATION_SEC, sr=16000):
    audio, _ = librosa.load(input_audio_path, sr=sr)
    chunk_samples = int(chunk_duration * sr)
    num_chunks = (len(audio) + chunk_samples - 1) // chunk_samples

    chunk_paths = []
    for i in range(num_chunks):
        start_sample = i * chunk_samples
        end_sample = min((i + 1) * chunk_samples, len(audio))
        chunk_audio = audio[start_sample:end_sample]

        temp_chunk_path = os.path.join(tempfile.gettempdir(), f"chunk_{i}.wav")
        sf.write(temp_chunk_path, chunk_audio, sr)
        chunk_paths.append(temp_chunk_path)

    return chunk_paths


def process_audio_and_combine(input_audio_path):
    # Split into chunks
    chunk_paths = split_audio(input_audio_path, sr=df_state.sr())
    print(f"Split audio into {len(chunk_paths)} chunks.")

    enhanced_chunks = []
    for i, chunk_path in enumerate(chunk_paths):
        print(f"Enhancing chunk {i + 1}/{len(chunk_paths)}: {chunk_path}")
        # Enhance chunk
        enhanced_path = enhance_audio_file(chunk_path)
        
        # Load enhanced chunk audio
        enhanced_audio, _ = librosa.load(enhanced_path, sr=df_state.sr())
        enhanced_chunks.append(enhanced_audio)

    # Concatenate all enhanced chunks
    combined_audio = np.concatenate(enhanced_chunks)

    # Prepare combined output path
    base_name = os.path.splitext(os.path.basename(input_audio_path))[0]
    output_dir = os.path.dirname(input_audio_path)
    combined_output_path = os.path.join(output_dir, f"{base_name}_ENHANCED_COMBINED.wav")

    # Save combined enhanced audio
    sf.write(combined_output_path, combined_audio, df_state.sr())

    # Optionally cleanup chunk files here if you want

    return combined_output_path



def enhance_video_file(input_video_path, out_path=None):
    """
    Extracts audio from a video, enhances it with DeepFilterNet2,
    and replaces the audio track in the video without re-encoding the video.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_audio_path = os.path.join(tmpdir, "extracted_audio.wav")
        enhanced_audio_path = os.path.join(tmpdir, "enhanced_audio.wav")

        # Extract audio with MoviePy
        video_clip = VideoFileClip(input_video_path)
        video_clip.audio.write_audiofile(raw_audio_path, fps=48000, codec="pcm_s16le")

        # Enhance audio (your custom function using DeepFilterNet2 + GPU)
        enhanced_audio_path = process_audio_and_combine(raw_audio_path)

        print("Finished enhancing audio. Saved enhanced audio to", enhanced_audio_path)

        # Define output path
        base_name, ext = os.path.splitext(os.path.basename(input_video_path))
        
        if out_path is None:
            output_video_path = os.path.join(
            os.path.dirname(input_video_path),
            f"{base_name}_ENHANCED_AUDIO{ext}"
            )
        else:
            # If out_path is a directory, save the video inside it
            if os.path.isdir(out_path):
                output_video_path = os.path.join(
                out_path,
                f"{base_name}_ENHANCED_AUDIO{ext}"
            )
            else:
                output_video_path = out_path

        # Replace audio in video WITHOUT re-encoding the video stream
        cmd = f'ffmpeg -y -i "{input_video_path}" -i "{enhanced_audio_path}" -c:v copy -map 0:v:0 -map 1:a:0 -shortest "{output_video_path}"'
        os.system(cmd)

        print("Video saved to:", output_video_path)
        return output_video_path

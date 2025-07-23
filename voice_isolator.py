"""
https://github.com/yuguochencuc/DeepFilterNet2
"""

import os
from df.enhance import enhance, init_df, load_audio, save_audio

if __name__ == "__main__":
    # 1. Load the DeepFilterNet model
    model, df_state, _ = init_df()

    # 2. Load your noisy audio file
    audio_path = "F:/deepfilternet/demo_noisy_record.wav"
    # Load audio, ensure it's at the correct sample rate (usually 48kHz for DeepFilterNet)
    audio, _ = load_audio(audio_path, sr=df_state.sr())

    # 3. Denoise the audio
    enhanced_audio = enhance(model, df_state, audio)

    # 4. Save the enhanced audio with the new filename format
    base_name = os.path.basename(audio_path)
    name, ext = os.path.splitext(base_name)
    enhanced_filename = f"{name}_ENHANCED{ext}"
    
    save_audio(enhanced_filename, enhanced_audio, df_state.sr())

    print(f"Denoised audio saved to {enhanced_filename}")
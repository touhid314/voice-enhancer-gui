from utils import enhance_audio_file, enhance_video_file
import os


############### SET INPUT AND OUTPUT FOLDER PATHS AND RUN THE SCRIPT ###############
folder_path = r"D:\Higher Study Admission Course\Touhid videos\records\#FINAL VIDEOS"
out_folder = r"D:\Higher Study Admission Course\Touhid videos\records\#FINAL VIDEOS\Enhanced Audio"
####################################################################################

for filename in os.listdir(folder_path):
    if filename.endswith(".mov") or filename.endswith(".mp4") or filename.endswith(".avi"):
        print(f"\t\t#### Processing file: {filename}")
        output_video_path = enhance_video_file(input_video_path=os.path.join(folder_path, filename), out_path=out_folder)

        print(f"Enhanced video saved to: {output_video_path}")


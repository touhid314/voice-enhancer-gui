import os

folder = r"D:\Higher Study Admission Course\Mehnaz videos\Enhanced Audio"

for filename in os.listdir(folder):
    old_path = os.path.join(folder, filename)

    # Skip directories
    if not os.path.isfile(old_path):
        continue

    name, ext = os.path.splitext(filename)

    # Only rename if "_ENHANCED_AUDIO" is in the filename
    if name.endswith("_ENHANCED_AUDIO"):
        new_name = name.replace("_ENHANCED_AUDIO", "") + ext
        new_path = os.path.join(folder, new_name)

        print(f"Renaming: {filename} -> {new_name}")
        os.rename(old_path, new_path)

print("✅ Renaming complete!")

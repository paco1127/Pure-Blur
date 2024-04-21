import os

folder_path = "uploads"  # Replace with the actual folder path

# Get the list of files in the folder
file_list = os.listdir(folder_path)

# Iterate over each file in the folder
for file_name in file_list:
    if file_name.lower().endswith(".jpg") and file_name.lower().startswith("censor_"):
        file_path = os.path.join(folder_path, file_name)
        os.remove(file_path)
        print(f"Deleted file: {file_name}")
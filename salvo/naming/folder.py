import os


def list_files_walk(start_path):
    file_list = []
    for root, dirs, files in os.walk(start_path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

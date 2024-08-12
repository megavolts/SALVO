import os


def list_folder_recursive(path):
    """
    Return a list of all files within a folder
    :param path: string, path to the folder
    :return: list of strings, containing the file path of each file
    """
    filelists = []
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            filelists.extend(list_folder_recursive(full_path))
        else:
            filelists.append(full_path)
    return filelists


def select_extension(filelists, extensions):
    """
    Return a list of files with selected extensions.
    :param filelists: list of string, containing filepaths
    :param extensions: string or list of string, extensions or list of extensions
    :return: list of string, containing the selected filepaths
    """

    if not isinstance(extensions, list):
        extensions = [extensions]
    return [f for f in filelists if f.split('.')[-1] in extensions]


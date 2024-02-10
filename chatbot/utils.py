import os

def get_project_directory():
    current_file_path = os.path.abspath(__file__)
    parent_directory = os.path.dirname(current_file_path)
    return os.path.dirname(parent_directory)

def get_path(path: str):
    """
    Get full path relative to project directory.
    """
    project_dir = get_project_directory()
    return os.path.join(project_dir, path)
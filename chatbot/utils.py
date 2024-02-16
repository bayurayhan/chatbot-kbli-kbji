import os
import re
import pandas as pd

def get_project_directory():
    current_file_path = os.path.abspath(__file__)
    parent_directory = os.path.dirname(current_file_path)
    return os.path.dirname(parent_directory)

def get_path(*path: str):
    """
    Get full path relative to project directory.
    """
    project_dir = get_project_directory()
    return os.path.join(project_dir, *path)

def read_specific_row(filename, row_number):
    df = pd.read_csv(filename)
    specific_row = df.iloc[row_number]
    return specific_row

def escape_characters(input_string):
    escaped_string = re.sub(r'([\_\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!])', r'\\\1', input_string)
    return escaped_string

def replace_starting_asterisk_with_dash(input_string):
    """
    Replaces a '*' at the beginning of a line with '-' using regular expressions.
    
    Parameters:
        input_string (str): The input string.
    
    Returns:
        str: The modified string with '*' replaced with '-' at the beginning of lines.
    """
    return re.sub(r'^\* ', '- ', input_string, flags=re.MULTILINE)

def gemini_markdown_to_markdown(input):
    input = remove_trailing_asterisks(input)
    input = replace_starting_asterisk_with_dash(input)
    input = escape_characters(input)
    return input

def remove_trailing_asterisks(input_string):
    """
    Removes trailing asterisks from a string and replaces them with only one asterisk.
    
    Parameters:
        input_string (str): The input string with trailing asterisks.
    
    Returns:
        str: The modified string with only one asterisk at the end.
    """
    return re.sub(r'\*+', '*', input_string)
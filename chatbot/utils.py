import os
import re
import pandas as pd
import csv

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
    escaped_string = re.sub(r'([\_\[\]\(\)\~\>\#\+\-\=\|\{\}\.\!])', r'\\\1', input_string)
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

def remove_emojis(text):
    # Emoji ranges (from https://unicode.org/emoji/charts/full-emoji-list.html)
    emoji_pattern = re.compile(
        "["
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+"
    )
    return emoji_pattern.sub(r"", text)

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

def save_chat_history(chat_id, role, new_message):
    folder_hist = get_path("chatbot", "history")
    filename = os.path.join(folder_hist, f"{chat_id}.csv")
    os.makedirs(folder_hist, exist_ok=True)
    
    # Check if the file exists, if not, create it
    if not os.path.isfile(filename):
        with open(filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["role", "content"])
            writer.writeheader()
    
    # Read existing content from the CSV file
    existing_data = []
    try:
        with open(filename, 'r', newline='') as file:
            reader = csv.DictReader(file)
            existing_data = list(reader)
    except FileNotFoundError:
        pass  # File doesn't exist yet, so no existing data

    # Append new message and keep only the latest 5 messages
    existing_data.append({"role": role, "content": new_message})
    latest_messages = existing_data[-10:]

    # Write the latest messages back to the CSV file
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["role", "content"])
        writer.writeheader()
        writer.writerows(latest_messages)

def read_chat_history(chat_id, use_dict=True, n=5) -> list[dict]:
    folder_hist = get_path("chatbot", "history")
    filename = os.path.join(folder_hist, f"{chat_id}.csv")
    chat_history = []
    try:
        with open(filename, 'r', newline='') as file:
            reader = csv.DictReader(file)
            if use_dict:
                for row in reader:
                    chat_history.append(row)
            else:
                for row in reader:
                    chat_history.append(row["content"])
    except FileNotFoundError:
        print("Chat history file not found.")
    return chat_history[-n:]


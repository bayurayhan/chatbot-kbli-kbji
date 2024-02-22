import os
import requests
import zipfile
from chatbot.utils import *

def download_and_extract(url, save_path):
    # Download the file
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print("Download complete.")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        return

    # Extract the file
    with zipfile.ZipFile(save_path, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(save_path))
    print("Extraction complete.")

if __name__ == "__main__":
    file_url = "https://github.com/bayurayhan/chatbot-kbli-kbji/releases/download/v0.1/data.zip"
    save_path = get_path("chatbot", "data", "data.zip")
    download_and_extract(file_url, save_path)

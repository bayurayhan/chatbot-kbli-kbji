import os
import requests
import zipfile
from tqdm import tqdm
from chatbot.utils import *

def download_and_extract(url, save_path):
    # Download the file
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 KB
    progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)

    with open(save_path, 'wb') as f:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            f.write(data)

    progress_bar.close()
    print("Download complete.")

    # Extract the file
    with zipfile.ZipFile(save_path, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(save_path))
    print("Extraction complete.")

if __name__ == "__main__":
    file_url = "https://github.com/bayurayhan/chatbot-kbli-kbji/releases/download/v0.1/data.zip"
    save_path = get_path("chatbot", "data", "data.zip")
    download_and_extract(file_url, save_path)

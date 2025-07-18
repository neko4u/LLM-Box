import os
import requests
import json

class DataManager:
    def __init__(self, storage_path):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)

    def download_file(self, url, filename):
        response = requests.get(url)
        if response.status_code == 200:
            file_path = os.path.join(self.storage_path, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return file_path
        else:
            raise Exception(f"Failed to download file from {url}")

    def save_config(self, config, filename):
        file_path = os.path.join(self.storage_path, filename)
        with open(file_path, 'w') as f:
            json.dump(config, f)

    def load_config(self, filename):
        file_path = os.path.join(self.storage_path, filename)
        with open(file_path, 'r') as f:
            return json.load(f)

    def list_files(self):
        return os.listdir(self.storage_path)
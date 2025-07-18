import os
import requests
import hashlib

def download_file(url, dest):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        raise Exception(f"Failed to download file from {url}")

def verify_file_integrity(file_path, expected_hash):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest() == expected_hash

def main():
    model_url = "https://example.com/path/to/model"  # Replace with actual model URL
    model_dest = os.path.join("models", "model.bin")  # Adjust destination as needed
    expected_hash = "expected_sha256_hash_here"  # Replace with actual expected hash

    os.makedirs(os.path.dirname(model_dest), exist_ok=True)

    try:
        download_file(model_url, model_dest)
        if verify_file_integrity(model_dest, expected_hash):
            print("Model downloaded and verified successfully.")
        else:
            print("Model integrity check failed.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
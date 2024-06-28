import os
import shutil
from pathlib import Path


def create_test_file(filename: str, directory: str):
    # Ensure the directory exists
    Path(directory).mkdir(parents=True, exist_ok=True)

    file_path = os.path.join(directory, filename)
    with open(file_path, "wb") as f:
        f.write(os.urandom(1024))  # Write 1KB of random data

    return file_path


def cleanup_directory(directory: str):
    try:
        shutil.rmtree(directory)
    except FileNotFoundError:
        pass  # Directory does not exist
    except Exception as e:
        print(f"Error cleaning up directory {directory}: {e}")

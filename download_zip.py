#!/usr/bin/env python3
"""
Script to download a zip file from the given Deel share link.
"""

import requests
from pathlib import Path
import os

def download_zip(url: str, output_dir: str):
    """
    Download a zip file from URL to the specified directory.
    
    Args:
        url: The URL to download from
        output_dir: Directory to save the file
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Download the file
    filename = "1.0.0.zip"
    file_path = output_path / filename
    
    print(f"Downloading from: {url}")
    print(f"Saving to: {file_path}")
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Get file size for progress tracking
        total_size = int(response.headers.get('content-length', 0))
        
        with open(file_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='', flush=True)
        
        print(f"\nDownload completed: {file_path}")
        return str(file_path)
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return None
    except (OSError, IOError) as e:
        print(f"Error writing file: {e}")
        return None


if __name__ == "__main__":
    import sys
    
    # Default URL and directory
    url = "https://share.deel.ai/public.php/dav/files/3ZyWamJWrqzCf74/?accept=zip"
    output_dir = "downloads"
    
    # Allow custom directory as command line argument
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]

    os.makedirs(output_dir, exist_ok=True)
    
    print(f"URL: {url}")
    print(f"Output directory: {output_dir}")
    print()
    
    download_zip(url, output_dir)

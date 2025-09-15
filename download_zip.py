#!/usr/bin/env python3
"""
Script to download a zip file, extract it, and organize the contents.
"""

import requests
from pathlib import Path
import os
import zipfile
import shutil


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


def extract_zip_recursive(zip_path: str, extract_dir: str):
    """
    Extract a zip file and recursively extract any zip files found inside.
    
    Args:
        zip_path: Path to the zip file to extract
        extract_dir: Directory to extract to
    """
    zip_file = Path(zip_path)
    extract_path = Path(extract_dir)
    
    # Create extraction directory with zip file name (without extension)
    zip_name = zip_file.stem
    target_dir = extract_path / zip_name
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Extracting {zip_file} to {target_dir}")
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        
        print(f"Extraction completed: {target_dir}")
        
        # Look for zip files in the extracted content and extract them recursively
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                if file.lower().endswith('.zip'):
                    zip_file_path = Path(root) / file
                    print(f"Found nested zip: {zip_file_path}")
                    extract_zip_recursive(str(zip_file_path), str(target_dir))
        
        return str(target_dir)
        
    except zipfile.BadZipFile as e:
        print(f"Error: Invalid zip file - {e}")
        return None
    except (OSError, IOError) as e:
        print(f"Error extracting zip: {e}")
        return None


def find_and_copy_infos_folders(source_dir: str, target_dir: str):
    """
    Find folders containing 'infos.md' files and copy them to the target directory.
    
    Args:
        source_dir: Directory to search in
        target_dir: Directory to copy folders to
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Searching for folders with 'infos.md' in: {source_path}")
    
    copied_folders = []
    
    # Walk through all directories
    for root, dirs, files in os.walk(source_path):
        # Check if current directory has 'infos.md'
        if 'infos.md' in files:
            folder_path = Path(root)
            folder_name = folder_path.name
            
            # Create target folder path
            target_folder = target_path / folder_name
            
            # Avoid copying if already exists (or add counter)
            counter = 1
            original_target = target_folder
            while target_folder.exists():
                target_folder = Path(f"{original_target}_{counter}")
                counter += 1
            
            print(f"Found folder with infos.md: {folder_path}")
            print(f"Copying to: {target_folder}")
            
            try:
                shutil.copytree(folder_path, target_folder)
                copied_folders.append(str(target_folder))
                print(f"Successfully copied: {folder_name}")
            except (OSError, IOError) as e:
                print(f"Error copying folder {folder_name}: {e}")
    
    print(f"\nCopied {len(copied_folders)} folders with infos.md files:")
    for folder in copied_folders:
        print(f"  - {folder}")
    
    return copied_folders


def main():
    """Main function to execute the complete workflow."""
    # Default URL and directory
    url = "https://share.deel.ai/public.php/dav/files/3ZyWamJWrqzCf74/?accept=zip"
    output_dir = "downloads"
    
    print("=== LARD Dataset Download and Organization ===")
    print(f"URL: {url}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Step 1: Download the zip file
    print("Step 1: Downloading zip file...")
    zip_path = download_zip(url, output_dir)
    if not zip_path:
        print("Download failed. Exiting.")
        return
    
    print()
    
    # Step 2: Extract the zip file recursively
    print("Step 2: Extracting zip file and nested zips...")
    extracted_path = extract_zip_recursive(zip_path, output_dir)
    if not extracted_path:
        print("Extraction failed. Exiting.")
        return
    
    print()
    
    # Step 3: Find and copy folders with infos.md
    print("Step 3: Finding and copying folders with infos.md...")
    copied_folders = find_and_copy_infos_folders(extracted_path, output_dir)
    
    print()
    print("=== Process Complete ===")
    print(f"Downloaded zip: {zip_path}")
    print(f"Extracted to: {extracted_path}")
    print(f"Organized datasets in: {output_dir}")
    print(f"Found and copied {len(copied_folders)} dataset folders")


if __name__ == "__main__":
    main()

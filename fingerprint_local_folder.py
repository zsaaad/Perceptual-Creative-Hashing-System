#!/usr/bin/env python3
"""
Script 1: Fingerprint Local Creatives

This script scans a local folder of images and generates a perceptual hash for each one,
saving the results to a CSV file for later matching with ad platform data.

Usage:
    python fingerprint_local_folder.py <folder_path>
    
Example:
    python fingerprint_local_folder.py /path/to/creative/folder
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional

import imagehash
import pandas as pd
from PIL import Image, UnidentifiedImageError


def is_image_file(filename: str) -> bool:
    """
    Check if a file is an image based on its extension.
    
    Args:
        filename: Name of the file to check
        
    Returns:
        True if the file is an image, False otherwise
    """
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    return Path(filename).suffix.lower() in image_extensions


def generate_hashes(folder_path: str) -> List[Dict[str, str]]:
    """
    Generate perceptual hashes for all images in the specified folder.
    
    Args:
        folder_path: Path to the folder containing images
        
    Returns:
        List of dictionaries containing filename and perceptual hash pairs
        
    Raises:
        FileNotFoundError: If the folder path doesn't exist
        PermissionError: If the folder cannot be accessed
    """
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    if not folder_path.is_dir():
        raise ValueError(f"Path is not a directory: {folder_path}")
    
    image_data = []
    processed_count = 0
    error_count = 0
    
    print(f"Scanning folder: {folder_path}")
    print("=" * 50)
    
    # Loop through every file in the given folder_path
    for file_path in folder_path.iterdir():
        if file_path.is_file() and is_image_file(file_path.name):
            try:
                # Open the image and calculate its perceptual hash
                with Image.open(file_path) as img:
                    # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Generate perceptual hash using imagehash
                    image_hash = imagehash.phash(img)
                    
                    # Append data to our list
                    image_data.append({
                        'filename': file_path.name,
                        'phash': str(image_hash),
                        'file_path': str(file_path),
                        'file_size': file_path.stat().st_size
                    })
                    
                    processed_count += 1
                    print(f"✓ Processed: {file_path.name}")
                    
            except UnidentifiedImageError:
                print(f"✗ Skipped (not a valid image): {file_path.name}")
                error_count += 1
            except Exception as e:
                print(f"✗ Error processing {file_path.name}: {str(e)}")
                error_count += 1
    
    print("=" * 50)
    print(f"Processing complete!")
    print(f"✓ Successfully processed: {processed_count} images")
    print(f"✗ Errors/Skipped: {error_count} files")
    
    return image_data


def save_to_csv(image_data: List[Dict[str, str]], output_file: str = "local_creative_hashes.csv") -> None:
    """
    Save the image data to a CSV file.
    
    Args:
        image_data: List of dictionaries containing image information
        output_file: Name of the output CSV file
    """
    if not image_data:
        print("No image data to save.")
        return
    
    # Convert the list to a pandas DataFrame
    df = pd.DataFrame(image_data)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"✓ Saved {len(image_data)} records to: {output_file}")
    
    # Display a preview of the data
    print("\nPreview of generated data:")
    print(df.head())


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Generate perceptual hashes for images in a local folder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fingerprint_local_folder.py /path/to/creatives
  python fingerprint_local_folder.py ./my_ads_folder
        """
    )
    
    parser.add_argument(
        "folder_path",
        help="Path to the folder containing image files"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="local_creative_hashes.csv",
        help="Output CSV filename (default: local_creative_hashes.csv)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        # Generate hashes for all images in the folder
        image_data = generate_hashes(args.folder_path)
        
        # Save results to CSV
        save_to_csv(image_data, args.output)
        
        if args.verbose:
            print(f"\nDetailed summary:")
            print(f"Total files processed: {len(image_data)}")
            if image_data:
                df = pd.DataFrame(image_data)
                print(f"File size range: {df['file_size'].min()} - {df['file_size'].max()} bytes")
                print(f"Hash length: {len(image_data[0]['phash'])} characters")
        
    except (FileNotFoundError, PermissionError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
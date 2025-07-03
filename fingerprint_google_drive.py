#!/usr/bin/env python3
"""
Script 1: Fingerprint Google Drive Creatives

This script connects to Google Drive API, scans a specified Google Drive folder for images,
and generates perceptual hashes for each one, saving the results to a CSV file for later
matching with ad platform data.

Usage:
    python fingerprint_google_drive.py <google_drive_folder_id>
    
Example:
    python fingerprint_google_drive.py 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
"""

import os
import sys
import argparse
import io
import logging
from typing import List, Dict, Optional

import imagehash
import pandas as pd
from PIL import Image, UnidentifiedImageError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('google_drive_fingerprint.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def authenticate_google_drive() -> Optional[object]:
    """
    Authenticate with Google Drive API using OAuth2.
    
    Returns:
        Google Drive service object if successful, None if failed
    """
    creds = None
    
    # The file token.json stores the user's access and refresh tokens,
    # and is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Failed to refresh credentials: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists('credentials.json'):
                logger.error("credentials.json file not found. Please download it from Google Cloud Console.")
                return None
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logger.error(f"Failed to authenticate: {e}")
                return None
        
        # Save the credentials for the next run
        try:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            logger.warning(f"Failed to save token: {e}")
    
    try:
        # Build the service object
        service = build('drive', 'v3', credentials=creds)
        logger.info("Successfully authenticated with Google Drive API")
        return service
    except Exception as e:
        logger.error(f"Failed to build service: {e}")
        return None


def is_image_mime_type(mime_type: str) -> bool:
    """
    Check if a file is an image based on its MIME type.
    
    Args:
        mime_type: MIME type of the file
        
    Returns:
        True if the file is an image, False otherwise
    """
    image_mime_types = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
        'image/bmp', 'image/tiff', 'image/webp', 'image/svg+xml'
    }
    return mime_type.lower() in image_mime_types


def download_image_from_drive(service: object, file_id: str) -> Optional[Image.Image]:
    """
    Download an image from Google Drive and return it as a PIL Image object.
    
    Args:
        service: Google Drive service object
        file_id: ID of the file to download
        
    Returns:
        PIL Image object if successful, None if failed
    """
    try:
        # Create a BytesIO object to store the downloaded file
        file_io = io.BytesIO()
        
        # Download the file
        request = service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(file_io, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                logger.debug(f"Download {int(status.progress() * 100)}%")
        
        # Reset the file pointer to the beginning
        file_io.seek(0)
        
        # Open the image from the BytesIO object
        image = Image.open(file_io)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        logger.debug(f"Successfully downloaded image: {file_id}")
        return image
        
    except HttpError as e:
        logger.warning(f"HTTP error downloading file {file_id}: {e}")
        return None
    except UnidentifiedImageError as e:
        logger.warning(f"Invalid image format for file {file_id}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error downloading file {file_id}: {e}")
        return None


def generate_hashes_from_drive(folder_id: str) -> List[Dict[str, str]]:
    """
    Generate perceptual hashes for all images in the specified Google Drive folder.
    
    Args:
        folder_id: Google Drive folder ID
        
    Returns:
        List of dictionaries containing filename and perceptual hash pairs
        
    Raises:
        ValueError: If folder_id is invalid
        Exception: If authentication or API calls fail
    """
    # Authenticate with Google Drive
    service = authenticate_google_drive()
    if not service:
        raise Exception("Failed to authenticate with Google Drive API")
    
    image_data = []
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"Scanning Google Drive folder: {folder_id}")
    print("=" * 60)
    
    try:
        # List all files in the folder
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType, size, webViewLink)",
            pageSize=1000
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print("No files found in the specified folder.")
            return image_data
        
        print(f"Found {len(files)} files in the folder")
        
        # Process each file
        for file in files:
            file_id = file['id']
            file_name = file['name']
            mime_type = file['mimeType']
            file_size = int(file.get('size', 0))
            web_link = file.get('webViewLink', '')
            
            try:
                # Check if the file is an image
                if not is_image_mime_type(mime_type):
                    logger.info(f"Skipping non-image file: {file_name} ({mime_type})")
                    print(f"⏭️  Skipped: {file_name} (not an image)")
                    skipped_count += 1
                    continue
                
                # Download and process the image
                image = download_image_from_drive(service, file_id)
                if image is None:
                    logger.warning(f"Failed to download image: {file_name}")
                    print(f"❌ Failed: {file_name} (download failed)")
                    error_count += 1
                    continue
                
                # Calculate perceptual hash
                image_hash = imagehash.phash(image)
                
                # Store the result
                image_data.append({
                    'filename': file_name,
                    'phash': str(image_hash),
                    'file_id': file_id,
                    'file_size': file_size,
                    'web_link': web_link
                })
                
                processed_count += 1
                print(f"✅ Processed: {file_name}")
                
            except Exception as e:
                logger.error(f"Error processing file {file_name}: {e}")
                print(f"❌ Error: {file_name} (processing error)")
                error_count += 1
        
        print("=" * 60)
        print(f"Processing complete!")
        print(f"✅ Successfully processed: {processed_count} images")
        print(f"⏭️  Skipped (not images): {skipped_count} files")
        print(f"❌ Errors: {error_count} files")
        print("=" * 60)
        
    except HttpError as e:
        logger.error(f"Google Drive API error: {e}")
        raise Exception(f"Google Drive API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    
    return image_data


def save_to_csv(image_data: List[Dict[str, str]], output_file: str = "google_drive_creative_hashes.csv") -> None:
    """
    Save the image data to a CSV file.
    
    Args:
        image_data: List of dictionaries containing image information
        output_file: Name of the output CSV file
    """
    if not image_data:
        print("No image data to save.")
        return
    
    try:
        # Convert the list to a pandas DataFrame
        df = pd.DataFrame(image_data)
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        logger.info(f"Saved {len(image_data)} records to: {output_file}")
        print(f"✅ Saved {len(image_data)} records to: {output_file}")
        
        # Display a preview of the data
        print("\nPreview of generated data:")
        print(df.head())
        
    except Exception as e:
        logger.error(f"Failed to save CSV file: {e}")
        raise


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Generate perceptual hashes for images in a Google Drive folder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Prerequisites:
  1. Download credentials.json from Google Cloud Console
  2. Enable Google Drive API in your Google Cloud project
  3. Place credentials.json in the same directory as this script

Examples:
  python fingerprint_google_drive.py 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
  python fingerprint_google_drive.py 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms -o my_hashes.csv
        """
    )
    
    parser.add_argument(
        "folder_id",
        help="Google Drive folder ID (found in the folder URL)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="google_drive_creative_hashes.csv",
        help="Output CSV filename (default: google_drive_creative_hashes.csv)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Check if credentials file exists
        if not os.path.exists('credentials.json'):
            print("❌ credentials.json file not found!")
            print("Please download it from Google Cloud Console and place it in this directory.")
            print("1. Go to https://console.cloud.google.com/")
            print("2. Create a project and enable Google Drive API")
            print("3. Create credentials (OAuth 2.0 Client ID)")
            print("4. Download the JSON file and rename it to credentials.json")
            sys.exit(1)
        
        # Generate hashes for all images in the Google Drive folder
        print("🔐 Authenticating with Google Drive...")
        image_data = generate_hashes_from_drive(args.folder_id)
        
        # Save results to CSV
        print("💾 Saving results to CSV...")
        save_to_csv(image_data, args.output)
        
        # Final summary
        print(f"\n🎉 Successfully processed and hashed {len(image_data)} Google Drive images!")
        
        if args.verbose and image_data:
            df = pd.DataFrame(image_data)
            print(f"\nDetailed summary:")
            print(f"Total files processed: {len(image_data)}")
            print(f"File size range: {df['file_size'].min()} - {df['file_size'].max()} bytes")
            print(f"Hash length: {len(image_data[0]['phash'])} characters")
        
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        print(f"❌ Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main() 
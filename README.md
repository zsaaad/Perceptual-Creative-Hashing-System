# Perceptual Creative Hashing System

A Python-based system that automatically matches ad creative files from a local folder (synced from Google Drive) with their corresponding ad IDs from the Meta and Google Ads platforms using perceptual hashing.

## Overview

This system solves the challenge of linking local creative files with their corresponding ad platform IDs by using perceptual hashing to create unique "fingerprints" for each image. Since the image content is the only common key between systems, we generate hashes for both local files and platform creatives, then match them to establish the connection.

## Project Structure

The system consists of four separate scripts that run in sequence:

1. **`fingerprint_local_folder.py`** - Scans local folder and generates perceptual hashes
2. **`fingerprint_google_drive.py`** - Scans Google Drive folder and generates perceptual hashes
3. **`fingerprint_ad_platforms.py`** - Retrieves creatives from Meta and Google Ads APIs and generates hashes
4. **`match_hashes.py`** - Matches local/Drive and platform hashes to link files with ad IDs

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd "Perceptual Creative Hashing System"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Script 1: Fingerprint Local Creatives

Generate perceptual hashes for all images in a local folder:

```bash
python3 fingerprint_local_folder.py /path/to/your/creatives/folder
```

**Options:**
- `-o, --output`: Specify output CSV filename (default: `local_creative_hashes.csv`)
- `-v, --verbose`: Enable verbose output with detailed statistics

**Examples:**
```bash
# Basic usage
python3 fingerprint_local_folder.py ./my_ads_folder

# Custom output file
python3 fingerprint_local_folder.py ./creatives -o my_hashes.csv

# Verbose output
python3 fingerprint_local_folder.py ./creatives -v
```

**Output:**
The script creates a CSV file (`local_creative_hashes.csv` by default) containing:
- `filename`: Original filename
- `phash`: Perceptual hash (64-character hexadecimal string)
- `file_path`: Full path to the file
- `file_size`: File size in bytes

### Script 2: Fingerprint Google Drive Creatives

Generate perceptual hashes for all images in a Google Drive folder:

```bash
python3 fingerprint_google_drive.py <google_drive_folder_id>
```

**Prerequisites:**
1. Download `credentials.json` from Google Cloud Console (see `google_drive_setup.md`)
2. Enable Google Drive API in your Google Cloud project
3. Place `credentials.json` in the same directory as the script

**Options:**
- `-o, --output`: Specify output CSV filename (default: `google_drive_creative_hashes.csv`)
- `-v, --verbose`: Enable verbose logging

**Examples:**
```bash
# Basic usage
python3 fingerprint_google_drive.py 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms

# Custom output file
python3 fingerprint_google_drive.py 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms -o my_drive_hashes.csv

# Verbose logging
python3 fingerprint_google_drive.py 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms -v
```

**Output:**
The script creates a CSV file (`google_drive_creative_hashes.csv` by default) containing:
- `filename`: Original filename
- `phash`: Perceptual hash (64-character hexadecimal string)
- `file_id`: Google Drive file ID
- `file_size`: File size in bytes
- `web_link`: Google Drive web link

### Script 3: Fingerprint Meta Ad Creatives

Generate perceptual hashes for all ad creatives from Meta Marketing API:

```bash
python3 fingerprint_ad_platforms.py <meta_ad_account_id> <google_customer_id>
```

**Prerequisites:**
Set the following environment variables:
```bash
export META_APP_ID=your_app_id
export META_APP_SECRET=your_app_secret
export META_ACCESS_TOKEN=your_access_token
```

**Options:**
- `-o, --output`: Specify output CSV filename (default: `platform_creative_hashes_META.csv`)
- `-v, --verbose`: Enable verbose logging

**Examples:**
```bash
# Basic usage (Meta only)
python3 fingerprint_ad_platforms.py act_123456789 1234567890 --meta-only

# Both platforms
python3 fingerprint_ad_platforms.py act_123456789 1234567890

# Custom output file
python3 fingerprint_ad_platforms.py act_123456789 1234567890 -o my_hashes.csv

# Verbose logging
python3 fingerprint_ad_platforms.py act_123456789 1234567890 -v
```

**Output:**
The script creates a CSV file (`platform_creative_hashes_ALL.csv` by default) containing:
- `ad_id`: Platform creative ID
- `platform`: Platform name ('Meta' or 'Google')
- `phash`: Perceptual hash (64-character hexadecimal string)
- `creative_name`: Creative name from platform
- `thumbnail_url`: URL of the creative thumbnail (Meta) or asset info (Google)

## Supported Image Formats

The system supports the following image formats:
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff)
- WebP (.webp)

## Technical Details

### Perceptual Hashing

The system uses the `imagehash` library with the `phash` (perceptual hash) algorithm, which:
- Resizes images to a standard size (32x32 pixels)
- Converts to grayscale
- Applies a discrete cosine transform
- Creates a 64-bit hash based on the low-frequency components

This approach is robust against:
- Minor image modifications (brightness, contrast, slight cropping)
- Different file formats
- Small compression artifacts

### Hash Matching

Perceptual hashes can be compared using Hamming distance to find similar images. Two images are considered matches if their hash difference is below a threshold (typically 5-10 bits for 64-bit hashes).

## Error Handling

The script includes comprehensive error handling for:
- Invalid folder paths
- Permission errors
- Corrupted or unsupported image files
- Memory issues with large images

## Performance Considerations

- The script processes images sequentially to avoid memory issues
- Large images are automatically resized during hash generation
- Progress indicators show processing status for large folders

## Next Steps

The following scripts will be implemented to complete the system:

1. **Google Ads Integration**: Extend Script 2 to include Google Ads API integration
2. **Matching Engine**: Create Script 3 to compare hashes and generate final mapping between local files and ad IDs

## Dependencies

- `imagehash`: Perceptual hashing library
- `pandas`: Data manipulation and CSV handling
- `Pillow`: Image processing
- `google-api-python-client`: Google Ads API integration
- `facebook-business`: Meta Marketing API integration

## License

[Add your license information here] 
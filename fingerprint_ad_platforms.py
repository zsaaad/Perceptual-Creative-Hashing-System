#!/usr/bin/env python3
"""
Script 2: Fingerprint Ad Platform Creatives (Meta & Google Ads Integration)

This script connects to both Meta Marketing API and Google Ads API, fetches all image-based 
ad creatives, and generates perceptual hashes for each one, saving the results to a CSV file.

Usage:
    python fingerprint_ad_platforms.py <meta_ad_account_id> <google_customer_id>
    
Example:
    python fingerprint_ad_platforms.py act_123456789 1234567890
"""

import os
import sys
import argparse
import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse
import time

import pandas as pd
import requests
import imagehash
from PIL import Image, UnidentifiedImageError
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.exceptions import FacebookRequestError
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import base64
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('meta_fingerprint.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def setup_meta_api(access_token: str, app_id: str, app_secret: str) -> None:
    """
    Initialize and authenticate with the Meta Marketing API.
    
    Args:
        access_token: Meta access token
        app_id: Meta app ID
        app_secret: Meta app secret
    """
    try:
        FacebookAdsApi.init(app_id, app_secret, access_token)
        logger.info("Successfully authenticated with Meta Marketing API")
    except Exception as e:
        logger.error(f"Failed to authenticate with Meta API: {e}")
        raise


def setup_google_ads_api() -> GoogleAdsClient:
    """
    Initialize and authenticate with the Google Ads API.
    
    Returns:
        GoogleAdsClient instance
        
    Raises:
        Exception: If authentication fails
    """
    try:
        # Google Ads API uses a YAML config file or environment variables
        # The client will automatically look for google-ads.yaml in the current directory
        # or use environment variables if the file doesn't exist
        client = GoogleAdsClient.load_from_storage()
        logger.info("Successfully authenticated with Google Ads API")
        return client
    except Exception as e:
        logger.error(f"Failed to authenticate with Google Ads API: {e}")
        raise


def decode_base64_image(base64_data: str) -> Optional[Image.Image]:
    """
    Decode a base64 encoded image and return it as a PIL Image object.
    
    Args:
        base64_data: Base64 encoded image data
        
    Returns:
        PIL Image object if successful, None if failed
    """
    try:
        # Decode base64 data
        image_data = base64.b64decode(base64_data)
        
        # Create image from bytes
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        logger.debug("Successfully decoded base64 image")
        return image
        
    except Exception as e:
        logger.warning(f"Failed to decode base64 image: {e}")
        return None


def download_image_from_url(url: str, timeout: int = 30) -> Optional[Image.Image]:
    """
    Download an image from a URL and return it as a PIL Image object.
    
    Args:
        url: URL of the image to download
        timeout: Request timeout in seconds
        
    Returns:
        PIL Image object if successful, None if failed
    """
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Open the image from the response content
        image = Image.open(response.raw)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        logger.debug(f"Successfully downloaded image from: {url}")
        return image
        
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to download image from {url}: {e}")
        return None
    except UnidentifiedImageError as e:
        logger.warning(f"Invalid image format from {url}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error downloading image from {url}: {e}")
        return None


def get_meta_hashes(ad_account_id: str) -> List[Dict[str, str]]:
    """
    Fetch all ad creatives from Meta Marketing API and generate perceptual hashes.
    
    Args:
        ad_account_id: Meta ad account ID (e.g., 'act_123456789')
        
    Returns:
        List of dictionaries containing ad_id, platform, and phash
    """
    meta_image_data = []
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    try:
        # Get the ad account object
        ad_account = AdAccount(ad_account_id)
        logger.info(f"Fetching creatives from ad account: {ad_account_id}")
        
        # Fetch all ad creatives
        creatives = ad_account.get_ad_creatives(
            fields=[
                'id',
                'thumbnail_url',
                'name',
                'object_story_spec'
            ],
            params={
                'limit': 1000  # Adjust based on your needs
            }
        )
        
        logger.info(f"Found {len(creatives)} creatives to process")
        print("=" * 60)
        print(f"Processing {len(creatives)} Meta ad creatives...")
        print("=" * 60)
        
        # Loop through each creative
        for creative in creatives:
            creative_id = creative.get('id')
            thumbnail_url = creative.get('thumbnail_url')
            creative_name = creative.get('name', 'Unnamed Creative')
            
            try:
                # Check if thumbnail_url exists and is not null
                if not thumbnail_url:
                    logger.info(f"Skipping creative {creative_id} ({creative_name}): No thumbnail URL")
                    print(f"⏭️  Skipped: {creative_name} (no thumbnail)")
                    skipped_count += 1
                    continue
                
                # Validate URL format
                parsed_url = urlparse(thumbnail_url)
                if not parsed_url.scheme or not parsed_url.netloc:
                    logger.warning(f"Invalid URL format for creative {creative_id}: {thumbnail_url}")
                    print(f"⚠️  Skipped: {creative_name} (invalid URL)")
                    skipped_count += 1
                    continue
                
                # Download the thumbnail image
                image = download_image_from_url(thumbnail_url)
                if image is None:
                    logger.warning(f"Failed to download image for creative {creative_id}")
                    print(f"❌ Failed: {creative_name} (download failed)")
                    error_count += 1
                    continue
                
                # Calculate perceptual hash
                image_hash = imagehash.phash(image)
                
                # Store the result
                meta_image_data.append({
                    'ad_id': creative_id,
                    'platform': 'Meta',
                    'phash': str(image_hash),
                    'creative_name': creative_name,
                    'thumbnail_url': thumbnail_url
                })
                
                processed_count += 1
                print(f"✅ Processed: {creative_name}")
                
                # Add a small delay to be respectful to the API
                time.sleep(0.1)
                
            except FacebookRequestError as e:
                logger.error(f"Facebook API error for creative {creative_id}: {e}")
                print(f"❌ Error: {creative_name} (API error)")
                error_count += 1
            except Exception as e:
                logger.error(f"Unexpected error processing creative {creative_id}: {e}")
                print(f"❌ Error: {creative_name} (unexpected error)")
                error_count += 1
        
        print("=" * 60)
        print(f"Processing complete!")
        print(f"✅ Successfully processed: {processed_count} creatives")
        print(f"⏭️  Skipped (no thumbnail): {skipped_count} creatives")
        print(f"❌ Errors: {error_count} creatives")
        print("=" * 60)
        
    except FacebookRequestError as e:
        logger.error(f"Facebook API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    
    return meta_image_data


def get_google_hashes(customer_id: str) -> List[Dict[str, str]]:
    """
    Fetch all image-based ad creatives from Google Ads API and generate perceptual hashes.
    
    Args:
        customer_id: Google Ads customer ID (without dashes)
        
    Returns:
        List of dictionaries containing ad_id, platform, and phash
    """
    google_image_data = []
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    try:
        # Setup Google Ads API client
        client = setup_google_ads_api()
        ga_service = client.get_service("GoogleAdsService")
        
        logger.info(f"Fetching creatives from Google Ads customer: {customer_id}")
        
        # Query for ad group ads with image assets
        query = """
            SELECT 
                ad_group_ad.ad.id,
                ad_group_ad.ad.name,
                asset.id,
                asset.name,
                asset.image_asset.full_size_image_url,
                asset.image_asset.data
            FROM ad_group_ad 
            WHERE ad_group_ad.ad.type IN ('RESPONSIVE_SEARCH_AD', 'RESPONSIVE_DISPLAY_AD', 'IMAGE_AD')
            AND asset.type = 'IMAGE'
        """
        
        # Execute the query
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id
        search_request.query = query
        search_request.page_size = 1000
        
        response = ga_service.search(request=search_request)
        
        logger.info(f"Found {len(response)} ad group ads to process")
        print("=" * 60)
        print(f"Processing Google Ads creatives...")
        print("=" * 60)
        
        # Process each ad group ad
        for row in response:
            try:
                ad_id = row.ad_group_ad.ad.id
                ad_name = row.ad_group_ad.ad.name or f"Ad {ad_id}"
                asset_id = row.asset.id
                asset_name = row.asset.name or f"Asset {asset_id}"
                
                # Try to get image data from base64 first, then URL
                image = None
                image_source = "base64"
                
                # Check if we have base64 image data
                if hasattr(row.asset, 'image_asset') and hasattr(row.asset.image_asset, 'data'):
                    image_data = row.asset.image_asset.data
                    if image_data:
                        image = decode_base64_image(image_data)
                
                # If no base64 data, try URL
                if image is None and hasattr(row.asset, 'image_asset') and hasattr(row.asset.image_asset, 'full_size_image_url'):
                    image_url = row.asset.image_asset.full_size_image_url
                    if image_url:
                        image = download_image_from_url(image_url)
                        image_source = "url"
                
                # Skip if no image data found
                if image is None:
                    logger.info(f"Skipping ad {ad_id} ({ad_name}): No image data")
                    print(f"⏭️  Skipped: {ad_name} (no image data)")
                    skipped_count += 1
                    continue
                
                # Calculate perceptual hash
                image_hash = imagehash.phash(image)
                
                # Store the result
                google_image_data.append({
                    'ad_id': str(ad_id),
                    'platform': 'Google',
                    'phash': str(image_hash),
                    'creative_name': ad_name,
                    'asset_name': asset_name,
                    'image_source': image_source
                })
                
                processed_count += 1
                print(f"✅ Processed: {ad_name} ({image_source})")
                
                # Add a small delay to be respectful to the API
                time.sleep(0.1)
                
            except GoogleAdsException as e:
                logger.error(f"Google Ads API error for ad {ad_id}: {e}")
                print(f"❌ Error: {ad_name} (API error)")
                error_count += 1
            except Exception as e:
                logger.error(f"Unexpected error processing ad {ad_id}: {e}")
                print(f"❌ Error: {ad_name} (unexpected error)")
                error_count += 1
        
        print("=" * 60)
        print(f"Processing complete!")
        print(f"✅ Successfully processed: {processed_count} creatives")
        print(f"⏭️  Skipped (no image): {skipped_count} creatives")
        print(f"❌ Errors: {error_count} creatives")
        print("=" * 60)
        
    except GoogleAdsException as e:
        logger.error(f"Google Ads API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    
    return google_image_data


def save_to_csv(data: List[Dict[str, str]], output_file: str = "platform_creative_hashes_ALL.csv") -> None:
    """
    Save the creative data to a CSV file.
    
    Args:
        data: List of dictionaries containing creative information
        output_file: Name of the output CSV file
    """
    if not data:
        logger.warning("No creative data to save.")
        print("⚠️  No creative data to save.")
        return
    
    try:
        # Convert the list to a pandas DataFrame
        df = pd.DataFrame(data)
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        logger.info(f"Saved {len(data)} records to: {output_file}")
        print(f"✅ Saved {len(data)} records to: {output_file}")
        
        # Display a preview of the data
        print("\nPreview of generated data:")
        print(df.head())
        
        # Show breakdown by platform
        if 'platform' in df.columns:
            platform_counts = df['platform'].value_counts()
            print(f"\nPlatform breakdown:")
            for platform, count in platform_counts.items():
                print(f"  {platform}: {count} creatives")
        
    except Exception as e:
        logger.error(f"Failed to save CSV file: {e}")
        raise


def load_environment_variables() -> Dict[str, str]:
    """
    Load Meta API credentials from environment variables.
    
    Returns:
        Dictionary containing access_token, app_id, and app_secret
    """
    required_vars = ['META_ACCESS_TOKEN', 'META_APP_ID', 'META_APP_SECRET']
    credentials = {}
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Missing required environment variable: {var}")
        credentials[var.lower().replace('meta_', '')] = value
    
    return credentials


def validate_google_ads_config() -> bool:
    """
    Validate that Google Ads API configuration is available.
    
    Returns:
        True if configuration is available, False otherwise
    """
    # Check for google-ads.yaml file
    if os.path.exists("google-ads.yaml"):
        return True
    
    # Check for environment variables
    required_vars = ['GOOGLE_ADS_CLIENT_ID', 'GOOGLE_ADS_CLIENT_SECRET', 'GOOGLE_ADS_REFRESH_TOKEN', 'GOOGLE_ADS_DEVELOPER_TOKEN']
    for var in required_vars:
        if not os.getenv(var):
            return False
    
    return True


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Generate perceptual hashes for Meta and Google Ads creatives",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables Required:
  META_ACCESS_TOKEN    Meta access token
  META_APP_ID          Meta app ID
  META_APP_SECRET      Meta app secret
  
  GOOGLE_ADS_CLIENT_ID         Google Ads client ID
  GOOGLE_ADS_CLIENT_SECRET     Google Ads client secret
  GOOGLE_ADS_REFRESH_TOKEN     Google Ads refresh token
  GOOGLE_ADS_DEVELOPER_TOKEN   Google Ads developer token

Examples:
  python fingerprint_ad_platforms.py act_123456789 1234567890
  python fingerprint_ad_platforms.py act_987654321 9876543210 -o my_hashes.csv
        """
    )
    
    parser.add_argument(
        "meta_ad_account_id",
        help="Meta ad account ID (e.g., act_123456789)"
    )
    
    parser.add_argument(
        "google_customer_id",
        help="Google Ads customer ID (e.g., 1234567890)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="platform_creative_hashes_ALL.csv",
        help="Output CSV filename (default: platform_creative_hashes_ALL.csv)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--meta-only",
        action="store_true",
        help="Process only Meta creatives (skip Google Ads)"
    )
    
    parser.add_argument(
        "--google-only",
        action="store_true",
        help="Process only Google Ads creatives (skip Meta)"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    all_platform_data = []
    
    try:
        # Process Meta creatives
        if not args.google_only:
            print("🔐 Loading Meta API credentials...")
            credentials = load_environment_variables()
            
            print("🔑 Authenticating with Meta Marketing API...")
            setup_meta_api(
                credentials['access_token'],
                credentials['app_id'],
                credentials['app_secret']
            )
            
            print(f"📊 Fetching Meta creatives from ad account: {args.meta_ad_account_id}")
            meta_data = get_meta_hashes(args.meta_ad_account_id)
            all_platform_data.extend(meta_data)
        
        # Process Google Ads creatives
        if not args.meta_only:
            if not validate_google_ads_config():
                print("⚠️  Google Ads configuration not found. Skipping Google Ads processing.")
                print("Please ensure google-ads.yaml exists or set required environment variables.")
            else:
                print(f"📊 Fetching Google Ads creatives from customer: {args.google_customer_id}")
                google_data = get_google_hashes(args.google_customer_id)
                all_platform_data.extend(google_data)
        
        # Save combined results to CSV
        print("💾 Saving results to CSV...")
        save_to_csv(all_platform_data, args.output)
        
        # Final summary
        total_creatives = len(all_platform_data)
        print(f"\n🎉 Successfully processed and hashed {total_creatives} ad creatives!")
        
        if all_platform_data:
            df = pd.DataFrame(all_platform_data)
            if 'platform' in df.columns:
                platform_counts = df['platform'].value_counts()
                print("Platform breakdown:")
                for platform, count in platform_counts.items():
                    print(f"  {platform}: {count} creatives")
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"❌ Configuration error: {e}")
        print("Please ensure all required environment variables are set.")
        sys.exit(1)
    except FacebookRequestError as e:
        logger.error(f"Meta API error: {e}")
        print(f"❌ Meta API error: {e}")
        sys.exit(1)
    except GoogleAdsException as e:
        logger.error(f"Google Ads API error: {e}")
        print(f"❌ Google Ads API error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
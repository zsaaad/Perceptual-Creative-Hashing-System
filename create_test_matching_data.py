#!/usr/bin/env python3
"""
Test script to create sample CSV files for testing the matching functionality.
"""

import pandas as pd

def create_test_local_hashes():
    """Create sample local creative hashes CSV."""
    local_data = [
        {
            'filename': 'ad_creative_1.png',
            'phash': '9a65659a9a65659a',
            'file_path': 'test_images/ad_creative_1.png',
            'file_size': 4523
        },
        {
            'filename': 'ad_creative_2.jpg',
            'phash': 'cb2434dbcb2434db',
            'file_path': 'test_images/ad_creative_2.jpg',
            'file_size': 5635
        },
        {
            'filename': 'banner_ad.png',
            'phash': 'cc3333cccc3333cc',
            'file_path': 'test_images/banner_ad.png',
            'file_size': 3785
        },
        {
            'filename': 'product_image.jpg',
            'phash': '857a7a85c57a3a85',
            'file_path': 'test_images/product_image.jpg',
            'file_size': 7981
        },
        {
            'filename': 'unmatched_local.png',
            'phash': '123456789abcdef0',
            'file_path': 'test_images/unmatched_local.png',
            'file_size': 3000
        }
    ]
    
    df = pd.DataFrame(local_data)
    df.to_csv('local_creative_hashes.csv', index=False)
    print("✅ Created local_creative_hashes.csv")

def create_test_platform_hashes():
    """Create sample platform creative hashes CSV."""
    platform_data = [
        {
            'ad_id': '123456789',
            'platform': 'Meta',
            'phash': '9a65659a9a65659a',
            'creative_name': 'Summer Sale Banner',
            'thumbnail_url': 'https://example.com/thumb1.jpg'
        },
        {
            'ad_id': '987654321',
            'platform': 'Meta',
            'phash': 'cb2434dbcb2434db',
            'creative_name': 'Product Showcase',
            'thumbnail_url': 'https://example.com/thumb2.jpg'
        },
        {
            'ad_id': '555666777',
            'platform': 'Meta',
            'phash': 'cc3333cccc3333cc',
            'creative_name': 'Banner Ad',
            'thumbnail_url': 'https://example.com/thumb3.jpg'
        },
        {
            'ad_id': '111222333',
            'platform': 'Meta',
            'phash': '857a7a85c57a3a85',
            'creative_name': 'Product Image',
            'thumbnail_url': 'https://example.com/thumb4.jpg'
        },
        {
            'ad_id': '999888777',
            'platform': 'Meta',
            'phash': 'abcdef1234567890',
            'creative_name': 'Unmatched Platform Ad',
            'thumbnail_url': 'https://example.com/thumb5.jpg'
        }
    ]
    
    df = pd.DataFrame(platform_data)
    df.to_csv('platform_creative_hashes_META.csv', index=False)
    print("✅ Created platform_creative_hashes_META.csv")

def main():
    """Create test data files."""
    print("🧪 Creating test data for matching...")
    
    create_test_local_hashes()
    create_test_platform_hashes()
    
    print("\n📊 Test data summary:")
    print("- 5 local creatives (4 should match, 1 unmatched)")
    print("- 5 platform creatives (4 should match, 1 unmatched)")
    print("- Expected: 4 successful matches")
    
    print("\n🎯 Ready to test matching functionality!")

if __name__ == "__main__":
    main() 
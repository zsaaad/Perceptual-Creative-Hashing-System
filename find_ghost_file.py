#!/usr/bin/env python3
"""
Ghost File Detection Script

This script identifies local creative files that don't have matching perceptual hashes
in the platform data, helping to isolate data discrepancies.
"""

import pandas as pd
import os

def load_csv_files():
    """Load the CSV files and return DataFrames."""
    try:
        # Check if files exist
        if not os.path.exists("local_creative_hashes.csv"):
            print("❌ local_creative_hashes.csv not found")
            return None, None
            
        if not os.path.exists("platform_creative_hashes_META.csv"):
            print("❌ platform_creative_hashes_META.csv not found")
            return None, None
        
        # Load the CSVs
        print("📂 Loading CSV files...")
        local_df = pd.read_csv("local_creative_hashes.csv")
        platform_df = pd.read_csv("platform_creative_hashes_META.csv")
        
        print(f"✅ Loaded {len(local_df)} local creatives")
        print(f"✅ Loaded {len(platform_df)} platform creatives")
        
        return local_df, platform_df
        
    except Exception as e:
        print(f"❌ Error loading CSV files: {e}")
        return None, None

def find_ghost_files(local_df, platform_df):
    """Find local creatives that don't match any platform creative."""
    print("\n🔍 Searching for ghost files...")
    
    # Find local phashes not present in platform phashes
    ghosts = local_df[~local_df['phash'].isin(platform_df['phash'])]
    
    if not ghosts.empty:
        print(f"\n👻 Found {len(ghosts)} ghost file(s):")
        print("-" * 40)
        for _, row in ghosts.iterrows():
            print(f"📁 {row['filename']}")
            print(f"   Hash: {row['phash']}")
            print(f"   Path: {row['file_path']}")
            print(f"   Size: {row['file_size']} bytes")
            print()
    else:
        print("\n✅ No ghost files found - all local creatives have platform matches!")
    
    return ghosts

def main():
    """Main execution function."""
    print("👻 Ghost File Detection")
    print("=" * 30)
    
    # Load CSV files
    local_df, platform_df = load_csv_files()
    
    if local_df is None or platform_df is None:
        print("\n❌ Cannot proceed without both CSV files.")
        print("Please ensure both Script 1 and Script 2 have been run successfully.")
        return
    
    # Find ghost files
    ghosts = find_ghost_files(local_df, platform_df)
    
    # Summary
    print("=" * 30)
    print("📊 Summary:")
    print(f"   Total local creatives: {len(local_df)}")
    print(f"   Total platform creatives: {len(platform_df)}")
    print(f"   Ghost files found: {len(ghosts)}")
    print(f"   Successful matches: {len(local_df) - len(ghosts)}")

if __name__ == "__main__":
    main() 
# Google Drive API Setup Guide

This guide will help you set up Google Drive API credentials for the `fingerprint_google_drive.py` script.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., "Creative Hashing System")
4. Click "Create"

## Step 2: Enable Google Drive API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Drive API"
3. Click on "Google Drive API"
4. Click "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External
   - App name: "Creative Hashing System"
   - User support email: Your email
   - Developer contact information: Your email
   - Save and continue through the remaining steps
4. Back in "Create OAuth client ID":
   - Application type: Desktop application
   - Name: "Creative Hashing Desktop Client"
   - Click "Create"

## Step 4: Download Credentials

1. After creating the OAuth client ID, click "Download JSON"
2. Rename the downloaded file to `credentials.json`
3. Place `credentials.json` in the same directory as `fingerprint_google_drive.py`

## Step 5: Find Your Google Drive Folder ID

1. Open Google Drive in your browser
2. Navigate to the folder containing your creative images
3. The folder ID is in the URL:
   ```
   https://drive.google.com/drive/folders/FOLDER_ID_HERE
   ```
4. Copy the FOLDER_ID_HERE part

## Step 6: Run the Script

```bash
python3 fingerprint_google_drive.py FOLDER_ID_HERE
```

Example:
```bash
python3 fingerprint_google_drive.py 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

## First Run Authentication

On the first run:
1. A browser window will open
2. Sign in with your Google account
3. Grant permission to access your Google Drive
4. The script will save a `token.json` file for future use

## Troubleshooting

### "credentials.json not found"
- Make sure you downloaded the OAuth client credentials JSON file
- Rename it to `credentials.json`
- Place it in the same directory as the script

### "Access denied" or "Permission denied"
- Make sure the Google Drive folder is shared with your Google account
- Check that you have read access to the folder

### "API not enabled"
- Go back to Google Cloud Console
- Make sure Google Drive API is enabled in your project

## Security Notes

- Keep `credentials.json` and `token.json` secure
- Don't commit these files to version control
- The script only requests read-only access to Google Drive 
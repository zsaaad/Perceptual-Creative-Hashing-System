#!/bin/bash

echo "🔐 Meta API Environment Variables Setup"
echo "======================================"
echo ""

# Check if environment variables are already set
if [ -n "$META_APP_ID" ]; then
    echo "✅ META_APP_ID is already set"
else
    echo "❌ META_APP_ID is not set"
fi

if [ -n "$META_APP_SECRET" ]; then
    echo "✅ META_APP_SECRET is already set"
else
    echo "❌ META_APP_SECRET is not set"
fi

if [ -n "$META_ACCESS_TOKEN" ]; then
    echo "✅ META_ACCESS_TOKEN is already set"
else
    echo "❌ META_ACCESS_TOKEN is not set"
fi

echo ""
echo "To set these variables, run the following commands:"
echo ""
echo "export META_APP_ID='1217038233303450'"
echo "export META_APP_SECRET='00428d6070340db4f26807642fb7d160'"
echo "export META_ACCESS_TOKEN='EAARS48uSZBZAoBOZCMRJlaSMfjmpHoPzDwZCztWXlmpMBSIgxxz5lyB4VUAt5ZCOSGh1Ya1oxkNGFoNhkRlOU6gUiBeq93wyIYznkPhliBjMoRRKuCxJiTTZAznzWeZAvkLgmGoQyzEBZAlzT1kCDoVftdH2iwqGXiQBsMxrVBnIMS9EsNZBXwOEQf8XoCGZCY4bENgqQZD'"
echo ""
echo "Or edit this script and uncomment the lines below:"
echo ""

# Uncomment and edit these lines with your actual credentials
# export META_APP_ID='your_app_id_here'
# export META_APP_SECRET='your_app_secret_here'
# export META_ACCESS_TOKEN='your_access_token_here'

echo "After setting the variables, you can test them with:"
echo "source setup_env.sh"
echo ""
echo "Then run your script:"
echo "python3 fingerprint_ad_platforms.py act_914776398650594 1234567890 --meta-only" 
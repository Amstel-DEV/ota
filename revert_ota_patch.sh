#!/bin/bash

image_helper="/lib/waydroid/tools/helpers/images.py"
ota_channel="/lib/waydroid/tools/config/__init__.py"

# Check if target files are present
if [[ ! -f "$image_helper" ]]; then
    echo "Waydroid is not properly installed, Please Reinstall Waydroid..."
    exit 1
fi

if [ ! -f "$ota_channel" ]; then
    echo "Waydroid is not properly installed, Please Reinstall Waydroid..."
    exit 1
fi

# Revert changes in images.py (uncomment sha256sum validation)
sed -i \
    -e '38,45 s/^# \?//' \
    -e '67,74 s/^# \?//' \
    "$image_helper"

# Revert OTA Channels to official URLs
sed -i \
    -e 's|https://amstel-dev\.github\.io/ota/system|https://ota.waydro.id/system|g' \
    -e 's|https://amstel-dev\.github\.io/ota/vendor|https://ota.waydro.id/vendor|g' \
    "$ota_channel"

echo "Waydroid patch has been reverted to official settings."
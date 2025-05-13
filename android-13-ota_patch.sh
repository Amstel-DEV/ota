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

# Patching images.py to bypass sha256sum validation
sed -i \
    -e '38,45 s/^[[:space:]]*/&# /' \
    -e '67,74 s/^[[:space:]]*/&# /' \
    "$image_helper"

# Patching OTA Channels to Android 13 OTA Non-Official Channel
sed -i \
    -e 's|https://ota\.waydro\.id/system|https://amstel-dev.github.io/ota/system|g' \
    -e 's|https://ota\.waydro\.id/vendor|https://amstel-dev.github.io/ota/vendor|g' \
    "$ota_channel"

echo "Waydroid Channels has been patched..."
#!/bin/bash

image_helper="/lib/waydroid/tools/helpers/images.py"
ota_channel="/lib/waydroid/tools/config/__init__.py"

# Ensure target files exist
function check_files() {
    clear
    if [[ ! -f "$image_helper" || ! -f "$ota_channel" ]]; then
        echo "Waydroid is not properly installed. Please reinstall Waydroid..."
        exit 1
    fi
}

# Apply patch
function patch_waydroid() {
    clear
    check_files

    echo "Patching Waydroid OTA channels and disabling sha256 validation..."
    echo 

    if grep -q "^[[:space:]]*#.*sha256sum" "$image_helper"; then
        echo "images.py already patched. Skipping..."
    else
        sed -i \
            -e '41,47 s/^[[:space:]]*/&# /' \
            -e '71,77 s/^[[:space:]]*/&# /' \
            "$image_helper"
        echo "images.py patch applied."
    fi

    if grep -q "amstel-dev.github.io" "$ota_channel"; then
        echo "OTA URLs already patched. Skipping..."
    else
        sed -i \
            -e 's|https://ota\.waydro\.id/system|https://amstel-dev.github.io/ota/system|g' \
            -e 's|https://ota\.waydro\.id/vendor|https://amstel-dev.github.io/ota/vendor|g' \
            "$ota_channel"
        echo
        echo "OTA URLs patched to unofficial source."
    fi
    echo ""
    echo ""
    read -p "Press enter to continue..."
}

# Restore Official Channels & Configurations
function restore_waydroid() {
    clear
    check_files

    echo "Reverting Waydroid to official settings..."
    echo 

    if grep -q "^[[:space:]]*#.*sha256sum" "$image_helper"; then
        sed -i \
            -e '41,47 s/^# \?//' \
            -e '71,77 s/^# \?//' \
            "$image_helper"
        echo "images.py restored."
    else
        echo "images.py is already in official state. Skipping..."
    fi

    if grep -q "amstel-dev.github.io" "$ota_channel"; then
        sed -i \
            -e 's|https://amstel-dev\.github\.io/ota/system|https://ota.waydro.id/system|g' \
            -e 's|https://amstel-dev\.github\.io/ota/vendor|https://ota.waydro.id/vendor|g' \
            "$ota_channel"
        echo
        echo "OTA URLs reverted to official Waydroid sources."
    else
        echo
        echo "OTA URLs are already official. Skipping..."
    fi
    echo ""
    echo ""
    read -p "Press enter to continue..."
}

# Show about info
function show_about() {
    clear
    echo "Android 13 OTA for Waydroid (Unofficial)"
    echo
    echo "This is an unofficial OTA server and patch tool for running Android 13 (Lineage 20) builds on Waydroid."
    echo "It allows users to automatically fetch and install Android 13 system and vendor images via OTA,"
    echo "even though these builds are not yet available in the official Waydroid OTA channels."
    echo
    echo "This project is community-maintained and is not affiliated with the official Waydroid project."
    echo
    echo "|= = = = = = = = = = = = = =// OTA Servers \\\\= = = = = = = = = = = = = = =|"
    echo "|   - OTA System Channel: https://amstel-dev.github.io/ota/system         |"
    echo "|   - OTA Vendor Channel: https://amstel-dev.github.io/ota/vendor         |"
    echo "|= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =|"
    echo
    echo "- Amstel-Dev"
    echo
    echo "1. Back to main-menu"
    echo "Q. Exit the program"
    echo

    while true; do
        read -p "Select an option: " about_choice
        case "$about_choice" in
            1) return ;;
            [Qq]) echo "Exiting..."; exit 0 ;;
            *) 
                echo "Invalid Input, Try Again..."; sleep 1;;
        esac
    done
}

# Main loop
while true; do
    clear
    echo "Waydroid Android 13 OTA Patcher"
    echo "By: Amstel-Dev"
    echo
    echo "1. Patch OTA Channels"
    echo "2. Restore Official OTA Channels & Settings"
    echo "3. About"
    echo
    echo "Q. Exit the program"
    echo

    read -p "Select an option: " choice
    case "$choice" in
        1) patch_waydroid ;;
        2) restore_waydroid ;;
        3) show_about ;;
        [Qq]) echo "Exiting..."; exit 0 ;;
        *) 
            echo "Invalid Input, Try Again..."
            sleep 3
            ;;
    esac
done

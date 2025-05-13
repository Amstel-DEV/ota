# 🚀 Android 13 OTA for Waydroid (Unofficial)

This is an **unofficial OTA server and patch tool** for running **Android 13 (Lineage 20) builds** on [Waydroid](https://waydro.id). It allows users to automatically fetch and install Android 13 system and vendor images via OTA, even though these builds are not yet available in the official Waydroid OTA channels.

> 📢 This project is community-maintained and is not affiliated with the official Waydroid project.

---

## 🌐 OTA Server

- **OTA System Channel**: [https://amstel-dev.github.io/ota/system](https://amstel-dev.github.io/ota/system)
- **OTA Vendor Channel**: [https://amstel-dev.github.io/ota/vendor](https://amstel-dev.github.io/ota/vendor)

## 🛠️ Patch Script

To redirect your Waydroid installation to use the unofficial OTA channel, use the provided script:

### 🔧 `android-13-ota_patch.sh`
```
curl -L https://amstel-dev.github.io/ota/android-13-ota_patch.sh | sudo bash
```
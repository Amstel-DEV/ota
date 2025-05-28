# -----------------------------------------------------------------------------
# Copyright (c) 2025 Amstel-DEV
# Developer: Amstel-DEV
# GitHub: https://github.com/Amstel-DEV
#
# Purpose:
# This script is designed for the Waydroid Android 13 Non-Official OTA Server
# project (https://github.com/Amstel-DEV/ota). It automates the retrieval,
# parsing, and organization of Waydroid LineageOS build files from SourceForge
# RSS feeds.
#
# It extracts metadata from filenames (version, date, architecture, ROM type,
# component), groups them by component type, architecture, and ROM type, sorts
# them by date, and generates JSON manifests. These JSON files are used by the
# OTA system to track available updates and provide OTA packages efficiently.
#
# Integration:
# This script is triggered by a GitHub Actions workflow (auto-update.yml) every
# 6 hours or manually. Upon running, it fetches the latest files, updates the
# JSON manifests, and commits/pushes changes back to the repository.
#
# How it works:
# 1. Defines supported architectures and base RSS feed URLs for system and vendor.
# 2. Downloads RSS feed entries, extracting file URLs and titles.
# 3. Parses filenames with regex to extract build metadata.
# 4. Filters out invalid or old builds.
# 5. Groups and sorts entries, creating organized JSON manifests per component,
#    architecture, and ROM type.
# 6. Saves JSON files in the 'system/lineage/' and 'vendor/' directories.
# 7. Workflow commits updated JSON manifests automatically.
#
# This setup ensures the OTA server repository stays updated with the latest
# build info for seamless OTA delivery of Waydroid images.
# -----------------------------------------------------------------------------

import os
import re
import json
import hashlib
import feedparser
from datetime import datetime

ARCHS = [
    "waydroid_arm",
    "waydroid_arm64",
    "waydroid_arm64_only",
    "waydroid_x86",
    "waydroid_x86_64",
    "waydroid_x86_64_only",
]

RSS_BASE = "https://sourceforge.net/projects/waydroid/rss?path=/images/"

def fetch_sourceforge_rss_file_list(rss_url):
    feed = feedparser.parse(rss_url)
    files = []
    for entry in feed.entries:
        url = entry.link
        filename = url.split('/')[-2] if url.endswith('/download') else url.split('/')[-1]
        title = entry.title
        files.append((title, url))
    return files

def parse_filename(filename):
    fname = os.path.basename(filename)

    pattern = re.compile(
        r"lineage-(\d+\.\d+)-(\d{8})-([A-Z0-9_]+)-(" + "|".join(map(re.escape, ARCHS)) + r")-(system|vendor|boot|recovery)\.zip"
    )
    m = pattern.search(fname)
    if not m:
        pattern2 = re.compile(
            r"lineage-(\d+\.\d+)-([A-Z0-9_]+)-(" + "|".join(map(re.escape, ARCHS)) + r")-(system|vendor|boot|recovery)\.zip"
        )
        m2 = pattern2.search(fname)
        if not m2:
            return None
        version, romtype, arch, component = m2.groups()
        dt_int = 0
    else:
        version, date_str, romtype, arch, component = m.groups()
        dt_obj = datetime.strptime(date_str, "%Y%m%d")
        dt_int = int(dt_obj.timestamp())

    try:
        version_float = float(version)
    except Exception:
        return None
    if version_float < 20.0:
        return None

    return {
        "version": version,
        "datetime": dt_int,
        "romtype": romtype,
        "arch": arch,
        "component_type": component,
        "filename": filename,
    }

def get_file_id(url):
    return hashlib.sha256(url.encode('utf-8')).hexdigest()

def ensure_dir_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    grouped = {}

    COMPONENTS = ["system", "vendor"]

    for component in COMPONENTS:
        rss_url = RSS_BASE + component + "/"
        print(f"Fetching RSS feed for: {component} ...")
        files = fetch_sourceforge_rss_file_list(rss_url)

        for title, url in files:
            info = parse_filename(title)
            if info is None:
                continue

            if component != info["component_type"]:
                continue

            info["url"] = url
            info["id"] = get_file_id(url)

            key = (info["component_type"], info["arch"], info["romtype"])
            grouped.setdefault(key, [])
            grouped[key].append(info)

    for (component_type, arch, romtype), items in grouped.items():
        items.sort(key=lambda x: x["datetime"], reverse=True)

        out_data = {"response": []}
        for item in items:
            out_item = {
                "datetime": item["datetime"],
                "filename": os.path.basename(item["filename"]),
                "id": item["id"],
                "romtype": item["romtype"],
                "url": item["url"],
                "version": item["version"],
            }
            out_data["response"].append(out_item)

        if component_type == "vendor":
            out_dir = os.path.join("vendor", arch)
        else:
            out_dir = os.path.join("system", "lineage", arch)

        ensure_dir_exists(out_dir)

        out_json = os.path.join(out_dir, f"{romtype}.json")

        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(out_data, f, indent=4)

        print(f"Wrote {len(items)} entries to {out_json}")

    # --- 404.html LIST UPDATER ---
    try:
        with open("404.html", "r", encoding="utf-8") as f:
            html = f.read()

        def generate_html_list(grouped, component_type):
            blocks = []
            for arch in ARCHS:
                items = [
                    item for (ctype, a, _), lst in grouped.items()
                    if ctype == component_type and a == arch
                    for item in lst
                ]
                if not items:
                    continue

                # Get latest item per (arch, romtype)
                latest_per_romtype = {}
                for item in sorted(items, key=lambda x: x["datetime"], reverse=True):
                    rt = item["romtype"]
                    if rt not in latest_per_romtype:
                        latest_per_romtype[rt] = item

                lines = "\n".join(
                    f'<li>Lineage-{item["version"]}-{datetime.utcfromtimestamp(item["datetime"]).strftime("%Y%m%d")}-{item["romtype"]}</li>'
                    for item in latest_per_romtype.values()
                )
                block = f'<ul>\n<h4>{arch}</h4>\n{lines}\n</ul>'
                blocks.append(block)
            return "\n".join(blocks)

        system_html = generate_html_list(grouped, "system")
        vendor_html = generate_html_list(grouped, "vendor")

        # Replace system list
        html = re.sub(
            r'(<div class="list_system">.*?<div class="container">)(.*?)(</div>)',
            rf'\1\n{system_html}\n\3',
            html,
            flags=re.DOTALL
        )

        # Replace vendor list
        html = re.sub(
            r'(<div class="list_vendor">.*?<div class="container">)(.*?)(</div>)',
            rf'\1\n{vendor_html}\n\3',
            html,
            flags=re.DOTALL
        )

        with open("404.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("Updated 404.html with grouped arch-based image lists.")
    except FileNotFoundError:
        print("404.html not found — skipping HTML update.")

if __name__ == "__main__":
    main()

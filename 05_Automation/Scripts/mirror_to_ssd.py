import os
import subprocess

source = "/Users/gregpaulsen/Desktop/BigSkyAg"
target = "/Volumes/BigSkySSD/BigSkyAg"

if not os.path.exists(source):
    print("⏭ Skipping sync: Desktop BigSkyAg folder not found.")
else:
    print(f"🔁 Previewing sync {source} → {target}...")
    subprocess.run([
        "rsync", "-av", "--delete",
        "--exclude", "*.DS_Store",
        source + "/", target + "/"
    ])
    print("✅ SSD sync complete.")


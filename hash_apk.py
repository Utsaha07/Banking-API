
import hashlib
import os

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()

apk_path = "sample.apk"   # change this to your real APK filename

print("Current folder:", os.getcwd())

if not os.path.exists(apk_path):
    print(f"File not found: {apk_path}")
    print("Put the APK in this folder or change apk_path to the correct filename.")
else:
    apk_hash = calculate_sha256(apk_path)
    print("SHA-256 Hash of APK:")
    print(apk_hash)
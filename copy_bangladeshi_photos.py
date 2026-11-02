import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BRAIN_DIR = r"C:\Users\Shawon!\.gemini\antigravity\brain\679b3919-0a4a-45c6-bf86-b8f53d770aff"
UPLOAD_DIR = os.path.join(BRAIN_DIR, ".user_uploaded")

PHOTOS = {
    # Rayan Ahmed: 1st pic uploaded by user
    'rayan_ahmed.jpg': os.path.join(UPLOAD_DIR, 'media_1790969660967.png'),
    'rayan_ahmed.png': os.path.join(UPLOAD_DIR, 'media_1790969660967.png'),
    # Haji Abdul Karim: 2nd pic uploaded by user
    'haji_abdul_karim.jpg': os.path.join(UPLOAD_DIR, 'media_1790969799983.png'),
    'haji_abdul_karim.png': os.path.join(UPLOAD_DIR, 'media_1790969799983.png'),
    # Nusrat Jahan
    'nusrat_jahan.jpg': os.path.join(BRAIN_DIR, 'nusrat_jahan_1790967168441.jpg'),
    'fatema_begum.jpg': os.path.join(BRAIN_DIR, 'fatema_begum_1790967829834.jpg'),
}

TARGET_DIRS = [
    os.path.join(BASE_DIR, 'static', 'images', 'cases'),
    os.path.join(BASE_DIR, 'staticfiles', 'images', 'cases'),
    os.path.join(BASE_DIR, 'media', 'case_photos'),
]

for d in TARGET_DIRS:
    os.makedirs(d, exist_ok=True)
    for fname, src in PHOTOS.items():
        if os.path.exists(src):
            dst = os.path.join(d, fname)
            shutil.copy2(src, dst)
            print(f"Copied {fname} -> {d}")

print("All user-specified photos successfully copied!")

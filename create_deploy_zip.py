import os
import zipfile

def make_zip():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(base_dir, "aponjon_update.zip")
    
    # Exclude unnecessary or sensitive files
    exclude_dirs = {'__pycache__', '.git', '.vscode', '.idea', 'env', 'venv'}
    exclude_files = {'.DS_Store', 'aponjon_update.zip', 'db.sqlite3'} # exclude db.sqlite3 to protect live database
    
    print("📦 Packing updated Aponjon files into aponjon_update.zip...")
    count = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file in exclude_files or file.endswith('.pyc'):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                zipf.write(full_path, rel_path)
                count += 1

    print(f"✅ Success! Packed {count} files into:")
    print(f"👉 {zip_path}")
    print("\nNext step: Upload this 'aponjon_update.zip' to PythonAnywhere and unzip it!")

if __name__ == '__main__':
    make_zip()

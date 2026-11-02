#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aponjon_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Ensure authentic Bangladeshi dummy photos are copied into static & media
    try:
        import shutil
        _base = os.path.dirname(os.path.abspath(__file__))
        _brain = r"C:\Users\Shawon!\.gemini\antigravity\brain\679b3919-0a4a-45c6-bf86-b8f53d770aff"
        _upload = os.path.join(_brain, ".user_uploaded")
        _photos = {
            'haji_abdul_karim.jpg': os.path.join(_upload, 'media_1790969799983.png'),
            'haji_abdul_karim.png': os.path.join(_upload, 'media_1790969799983.png'),
            'rayan_ahmed.jpg': os.path.join(_upload, 'media_1790969660967.png'),
            'rayan_ahmed.png': os.path.join(_upload, 'media_1790969660967.png'),
            'nusrat_jahan.jpg': os.path.join(_brain, 'nusrat_jahan_1790967168441.jpg'),
            'fatema_begum.jpg': os.path.join(_brain, 'fatema_begum_1790967829834.jpg'),
        }
        for d in [os.path.join(_base, 'static', 'images', 'cases'), os.path.join(_base, 'staticfiles', 'images', 'cases'), os.path.join(_base, 'media', 'case_photos')]:
            os.makedirs(d, exist_ok=True)
            for fname, src in _photos.items():
                if os.path.exists(src):
                    dst = os.path.join(d, fname)
                    if not os.path.exists(dst) or os.path.getsize(dst) == 0:
                        shutil.copy2(src, dst)
        # Copy hero banners
        _hero_dark_src = os.path.join(_brain, 'aponjon_hero_dark_1791014999633.jpg')
        if os.path.exists(_hero_dark_src):
            for hd in [os.path.join(_base, 'static', 'images'), os.path.join(_base, 'staticfiles', 'images')]:
                os.makedirs(hd, exist_ok=True)
                for hname in ['aponjon_hero_dark.jpg', 'hero_family.jpg']:
                    hd_dst = os.path.join(hd, hname)
                    if not os.path.exists(hd_dst) or os.path.getsize(hd_dst) == 0:
                        shutil.copy2(_hero_dark_src, hd_dst)
    except Exception:
        pass

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()

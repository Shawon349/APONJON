"""
Self-contained setup and test runner for আপনজন (Aponjon).
Executes database migrations and generates all seed data.
"""
import os
import sys

def run_setup():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aponjon_project.settings')
    import django
    django.setup()

    from django.core.management import call_command
    print("=" * 60)
    print("🚀 Initializing আপনজন (Aponjon) Missing Persons Platform...")
    print("=" * 60)
    
    print("\n[1/3] Preparing static assets and illustrations...")
    import shutil
    from pathlib import Path
    src_hero = Path(r"C:\Users\Shawon!\.gemini\antigravity\brain\679b3919-0a4a-45c6-bf86-b8f53d770aff\.user_uploaded\media_1790183646362.jpg")
    dst_hero = Path(__file__).resolve().parent / 'static' / 'images' / 'aponjon_hero.jpg'
    if src_hero.exists():
        dst_hero.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_hero, dst_hero)
        print("  ✓ Hero illustration successfully installed into static/images/aponjon_hero.jpg")

    print("\n[2/3] Running database migrations...")
    call_command('migrate')

    print("\n[3/3] Seeding demo cases, police officers, and alerts...")
    call_command('setup_aponjon_demo')

    print("\n" + "=" * 60)
    print("✅ Database setup complete!")
    print("You can now start the web application with:")
    print("    python manage.py runserver")
    print("Open http://127.0.0.1:8000 in your browser.")
    print("=" * 60)

if __name__ == '__main__':
    run_setup()

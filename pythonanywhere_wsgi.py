# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# আপনজন (Aponjon) - PythonAnywhere WSGI Configuration
# 
# নির্দেশিকা:
# ১. PythonAnywhere এর "Web" ট্যাবে যান।
# ২. "WSGI configuration file" লিংকে ক্লিক করুন (/var/www/<আপনার_ইউজারনেম>_pythonanywhere_com_wsgi.py)
# ৩. সেখানে থাকা সকল লেখা মুছে নিচের কোডটি পেস্ট করুন।
# ৪. শুধু USERNAME ভ্যারিয়েবলে আপনার PythonAnywhere ইউজারনেমটি লিখুন।
# ৫. Save করে Web ট্যাবের বড় সবুজ "Reload" বাটনে ক্লিক করুন।
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import sys

# এখানে আপনার PythonAnywhere এর ইউজারনেম বসান (যেমন: 'shawon' বা আপনার একাউন্টের নাম)
USERNAME = 'YOUR_PYTHONANYWHERE_USERNAME'

# প্রজেক্ট ডিরেক্টরির পাথ
project_home = f'/home/{USERNAME}/Aponjon_mywebsite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# ডিজাঙ্গো সেটিংস মডিউল সেট করা
os.environ['DJANGO_SETTINGS_MODULE'] = 'aponjon_project.settings'

# WSGI অ্যাপ্লিকেশন লোড
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

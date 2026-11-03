
import os
import sys


USERNAME = 'YOUR_PYTHONANYWHERE_USERNAME'


project_home = f'/home/{USERNAME}/Aponjon_mywebsite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)


os.environ['DJANGO_SETTINGS_MODULE'] = 'aponjon_project.settings'


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

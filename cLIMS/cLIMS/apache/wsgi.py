import os, sys

apache_configuration= os.path.dirname(__file__)
project = os.path.dirname(apache_configuration)
workspace = os.path.dirname(project)
sys.path.append(workspace)
sys.path.append(project)


sys.path.append('/djangoProject')
os.environ['DJANGO_SETTINGS_MODULE'] = 'cLIMS.apache.override'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


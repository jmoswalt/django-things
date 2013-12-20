import os
import dotenv
dotenv.read_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

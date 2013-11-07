import dj_database_url
import sys
from os import environ, path, listdir
from . import env

PROJECT_ROOT = path.abspath(path.join(path.dirname(__file__), ".."))
APPS_ROOT = path.join(PROJECT_ROOT, 'apps')
sys.path.insert(0, APPS_ROOT)

# Debug option which is useful when working locally.
DEBUG = env('DEBUG', False)
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

# Django 1.5 required setting
ALLOWED_HOSTS = ['*']

# -------------------------------------- #
# DATABASES
# -------------------------------------- #

DATABASES = env('DATABASES', {'default': dj_database_url.config(default='postgres://localhost/django_things')})

DATABASES['default']['OPTIONS'] = {'autocommit': True}


# Make this unique, and don't share it with anybody.
SECRET_KEY = env('SECRET_KEY', 'bbj1#c30g@qm!=xhpcfk$!^dq#1@s#mr0!f@$cz2e*^1tuskr7')


# -------------------------------------- #
# THEME
# -------------------------------------- #

THEME = env('THEME', 'default_theme')
THEME_PATH = path.join(PROJECT_ROOT, 'themes', THEME)

TEMPLATE_DIRS = (
    path.join(THEME_PATH, 'templates'),
)

STATICFILES_DIRS = (
    path.join(THEME_PATH, 'static'),
)


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

REDACTOR_OPTIONS = {'lang': 'en'}
REDACTOR_UPLOAD = 'wysiwyg_uploads/'


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'things.context_processors.extras',
)

ROOT_URLCONF = 'conf.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'conf.wsgi.application'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.markup',
    'django.contrib.staticfiles',
    'django.contrib.redirects',
    'django.contrib.sitemaps',

    'storages',
    'django_medusa',

    'things',
    'things.pages',
    'things.snippets',

    'redactor',
    'django.contrib.admin',
)

THINGS_APPS = ()

# Load apps from local "apps" folder in project
THINGS_APPS += tuple(app for app in listdir(APPS_ROOT))

INSTALLED_APPS += THINGS_APPS


# -------------------------------------- #
# S3 STORAGE OPTIONS
# -------------------------------------- #

AWS_PRELOAD_METADATA = True

AWS_ACCESS_KEY = env('AWS_ACCESS_KEY', '')
AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', '')
STATIC_S3_PATH = "static"
FULL_STATIC_SITE = False
USE_STATIC_SITE = env('USE_STATIC_SITE', False)
if USE_STATIC_SITE:
    FULL_STATIC_SITE = env('FULL_STATIC_SITE', False)


# -------------------------------------- #
# MEDUSA OPTIONS
# -------------------------------------- #

MEDUSA_MULTITHREAD = False

if all([AWS_ACCESS_KEY,
        AWS_SECRET_ACCESS_KEY,
        AWS_STORAGE_BUCKET_NAME]):
    MEDUSA_RENDERER_CLASS = "django_medusa.renderers.S3StaticSiteRenderer"
    STATICFILES_STORAGE = 'things.s3_storages.StaticStorage'
else:
    MEDUSA_RENDERER_CLASS = "django_medusa.renderers.DiskStaticSiteRenderer"
    MEDUSA_DEPLOY_DIR = path.join(PROJECT_ROOT, 'html')


# -------------------------------------- #
# DEBUG OPTIONS
# -------------------------------------- #

if env('SENTRY_DSN', None):
    INSTALLED_APPS += ('raven.contrib.django',)

if env('DEBUG_TOOLBAR'):
    if 'debug_toolbar' not in INSTALLED_APPS:
        INSTALLED_APPS += ('debug_toolbar',)

    if 'debug_toolbar.middleware.DebugToolbarMiddleware' not in MIDDLEWARE_CLASSES:
        MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }
    INTERNAL_IPS = ('127.0.0.1',)

# -------------------------------------- #
# CACHE
# -------------------------------------- #

SITE_CACHE_KEY = env('SITE_CACHE_KEY', SECRET_KEY)
CACHE_PRE_KEY = env('CACHE_PRE_KEY', SITE_CACHE_KEY)
JOHNNY_MIDDLEWARE_KEY_PREFIX = CACHE_PRE_KEY

# Dummy Cache is the initial default caching used
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# LOCAL MEMCACHE
# Local memcached requires memcached to be running locally.
# Requires adding the following packages to requirements.txt:
# python-memcached==1.48
LOCAL_MEMCACHED_URL = env('LOCAL_MEMCACHED_URL')
if LOCAL_MEMCACHED_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': LOCAL_MEMCACHED_URL,
        }
    }

# HEROKU ADDON - MEMCACHE
# https://addons.heroku.com/memcache
# Requires adding the following packages to requirements.txt:
# pylibmc==1.2.2
# django-pylibmc-sasl==0.2.4
MEMCACHE_SERVERS = env('MEMCACHE_SERVERS')

if MEMCACHE_SERVERS:
    CACHES = {
        'default': {
            'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        }
    }

# HEROKU ADDON - MEMCACHIER
# https://addons.heroku.com/memcachier
# Requires adding the following packages to requirements.txt:
# pylibmc==1.2.2
# django-pylibmc-sasl==0.2.4
MEMCACHIER_SERVERS = env('MEMCACHIER_SERVERS')
MEMCACHIER_USERNAME = env('MEMCACHIER_USERNAME')
MEMCACHIER_PASSWORD = env('MEMCACHIER_PASSWORD')

USE_MEMCACHIER = all([MEMCACHIER_SERVERS,
                      MEMCACHIER_USERNAME,
                      MEMCACHIER_PASSWORD])

if USE_MEMCACHIER:
    environ['MEMCACHE_SERVERS'] = MEMCACHIER_SERVERS
    environ['MEMCACHE_USERNAME'] = MEMCACHIER_USERNAME
    environ['MEMCACHE_PASSWORD'] = MEMCACHIER_PASSWORD

    CACHES = {
        'default': {
            'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
            'LOCATION': MEMCACHIER_SERVERS,
            'BINARY': True,
        }
    }

# Caching defaults
CACHES['default']['TIMEOUT'] = 604800  # 1 week
CACHES['default']['JOHNNY_CACHE'] = True

# -------------------------------------- #
# EMAIL
# -------------------------------------- #

EMAIL_USE_TLS = env('EMAIL_USE_TLS', True)
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

EMAIL_BACKEND = env('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')

# HEROKU ADDON - SENDGRID
# https://addons.heroku.com/sendgrid
SENDGRID_USERNAME = env('SENDGRID_USERNAME')
SENDGRID_PASSWORD = env('SENDGRID_PASSWORD')

USE_SENDGRID = all([SENDGRID_USERNAME, SENDGRID_PASSWORD])

if USE_SENDGRID:
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = SENDGRID_USERNAME
    EMAIL_HOST_PASSWORD = SENDGRID_PASSWORD
    EMAIL_PORT = '587'

# HEROKU ADDON - MAILGUN
# https://addons.heroku.com/mailgun
MAILGUN_SMTP_SERVER = env('MAILGUN_SMTP_SERVER')
MAILGUN_SMTP_LOGIN = env('MAILGUN_SMTP_LOGIN')
MAILGUN_SMTP_PASSWORD = env('MAILGUN_SMTP_PASSWORD')
MAILGUN_SMTP_PORT = env('MAILGUN_SMTP_PORT')

USE_MAILGUN = all([MAILGUN_SMTP_SERVER,
                   MAILGUN_SMTP_LOGIN,
                   MAILGUN_SMTP_PASSWORD,
                   MAILGUN_SMTP_PORT])

if USE_MAILGUN:
    EMAIL_USE_TLS = True
    EMAIL_HOST = MAILGUN_SMTP_SERVER
    EMAIL_HOST_USER = MAILGUN_SMTP_LOGIN
    EMAIL_HOST_PASSWORD = MAILGUN_SMTP_PASSWORD
    EMAIL_PORT = MAILGUN_SMTP_PORT


DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
SERVER_EMAIL = env('SERVER_EMAIL', DEFAULT_FROM_EMAIL)


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

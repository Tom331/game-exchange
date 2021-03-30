"""~~~NOTES~~~
- procfile could use channel_layer instead of channels
- AUTH_USER_MODEL could be 'django_project.User'. Worked locally but not on heroku
- django.setup() seems ok at bottom of settings.py... docs say you only need it for standalone (non-webserver)
- If have to

"""
import mimetypes
import os

import django
import django_heroku


print('~~~At top of settings~~~ ')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'exhlfdat&vfum(-34*c2uroi(($ww(yo$9pv98=e6p^gl(-eoj' #todo: test removing this in own deployment

ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1']

mimetypes.add_type("text/css", ".css", True)

# Application definition
# Allows Django to look for models (for Databases)
INSTALLED_APPS = [
    'channels',
    'blog',
    'chat',
    'users',
    'crispy_forms',
    'dal',
    'dal_select2',
    'storages',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

DJANGO_SETTINGS_MODULE = 'django_project.settings'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        #DIRS: a list of directories where the engine should look for template source files, in search order.
        'DIRS': [os.path.join(BASE_DIR, ''), # root directory
                 'django_project/blog'], # templates in blog app
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_project.wsgi.application'
ASGI_APPLICATION = 'django_project.routing.application' # older version of django: 'django_project.routing.application'

DB_URL = os.environ['DATABASE_URL']
DATABASE_URL = DB_URL


DATABASES = { # Use this to use local test DB # todo: prod doesn't havea access to django_session...
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_REDIRECT_URL = 'blog-home'
LOGIN_URL = 'login'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS')

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

DEBUG = 'True'

django_heroku.settings(locals()) # todo: USED TO RUN LOCALHOST WITH DATABASE_URL (and other env settings)

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}

# CACHES = { # maybe need maybe not
#     "default": {
#          "BACKEND": "redis_cache.RedisCache",
#          "LOCATION": os.environ.get('REDIS_TLS_URL'),
#          "OPTIONS": {
#             "CONNECTION_POOL_KWARGS": {
#                 "ssl_cert_reqs": False
#             }
#         }
#     }
# }

DATA_UPLOAD_MAX_NUMBER_FIELDS = 4000
#django.setup() #todo maybe need... CAUSES ImportError: cannot import name 'User'





# ~~~NOT IN VERY-ACADEMY OR JUSTCHAT:~~~
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage' #i think this is breaking it

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")

# application = get_wsgi_application()
# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = os.environ.get('SECRET_KEY')

# AUTH_USER_MODEL='auth.User' # todo: this causes RuntimeError: populate() isnt reentrant

CUSTOM_TEMPLATES_DIR = os.path.join(BASE_DIR,'..', 'templates'),
# print('CUSTOM_TEMPLATES_DIR: ' + CUSTOM_TEMPLATES_DIR)


SETTINGS_PATH = os.path.join(os.path.dirname(__file__) ,'../templates').replace('\\','/')
TEMPLATE_DIRS = ( # deprecated
    os.path.join(SETTINGS_PATH, 'blog/templates'), # Django will look at the templates from templates/ directory under your project
)


"""~~~NOTES~~~
- procfile could use channel_layer instead of channels
- AUTH_USER_MODEL could be 'django_project.User'. Worked locally but not on heroku
- django.setup() seems ok at bottom of settings.py
- If have to

"""

import django
from django.core.wsgi import get_wsgi_application
from django.core.asgi import get_asgi_application
# from django.contrib.auth.models import User #todo: this causes ImproperlyConfigured: SECRET_KEY MUST NOT BE EMPTY
import os
import django_heroku
from django.apps import apps


print('~~~At top of settings~~~ ')
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
DJANGO_SETTINGS_MODULE = 'django_project.settings'

# OLD AUTH...
SECRET_KEY = 'exhlfdat&vfum(-34*c2uroi(($ww(yo$9pv98=e6p^gl(-eoj' #todo: test removing this in own deployment

# application = get_wsgi_application()
# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = 'True'

ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1']


# Application definition
# Allows Django to look for models (for Databases)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'channels',
    'dal',
    'dal_select2',
    # 'auth.models',
    'storages',
    'blog.apps.BlogConfig', #allows Django to correctly search your templates for the 'blog' app
    'users.apps.UsersConfig',
    # 'users.CustomUser',
    # 'chat.apps.ChatConfig',
    'chat.apps.ChatConfig',
]
# AUTH_USER_MODEL='auth.User' # todo: this causes RuntimeError: populate() isnt reentrant




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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# CUSTOM_TEMPLATES_DIR = os.path.join(BASE_DIR,'..', 'templates'),
# print('CUSTOM_TEMPLATES_DIR: ' + CUSTOM_TEMPLATES_DIR)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, '')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 'libraries': {
            #     'staticfiles':'chat.templatetags.__init__.py'
            # }
        },
    },
]

SETTINGS_PATH = os.path.join(os.path.dirname(__file__) ,'../templates').replace('\\','/')
TEMPLATE_DIRS = ( # deprecated
    os.path.join(SETTINGS_PATH, 'blog/templates'), # Django will look at the templates from templates/ directory under your project
)

# ~~~MESSAGES CONFIG~~~
WSGI_APPLICATION = 'django_project.wsgi.application'
ASGI_APPLICATION = 'django_project.asgi.application' # older version of django: 'django_project.routing.application'

# Channels redis config:
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            #"hosts": [('127.0.0.1', 6379)], or 'redis' #l ocal
            "hosts": ['rediss://:p628bf20dab326cedb30d4df129e9691dbb6e7e1f4486954eadbfdf77db854369@ec2-34-235-242-69.compute-1.amazonaws.com:25180'], # REDIS_TLS_URL #todo: confirm. Changed from "127.0.0.1" to 'redis'... found promising answer, changing this
            # 'redis://:p628bf20dab326cedb30d4df129e9691dbb6e7e1f4486954eadbfdf77db854369@ec2-34-235-242-69.compute-1.amazonaws.com:25179' REDIS_URL
        },
        # "ROUTING": "chat.routing.websocket_urlpatterns", #todo: add "ROUTING": "chat.routing.websocket_urlpatterns",
    },
}

CACHES = {
    "default": {
         "BACKEND": "redis_cache.RedisCache",
         "LOCATION": os.environ.get('REDIS_TLS_URL'),
         "OPTIONS": {
            "CONNECTION_POOL_KWARGS": {
                "ssl_cert_reqs": False
            }
        }
    }
}



# Database setting:
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
# This seems to be overwritten by the config var in Heroku
DATABASES = { # Use this to use local test DB
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Use Postgrest Database in Shrouded-Inlet
DB_URL = os.environ['DATABASE_URL']
DATABASE_URL = DB_URL


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/howto/static-files/

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

# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage' #i think this is breaking it

django_heroku.settings(locals())

DATA_UPLOAD_MAX_NUMBER_FIELDS = 4000
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfilescustom') #todo: may have to add own staticFileDir folder
]

# print('~~~before django.setup()~~~')
django.setup()
# print('~~~after django.setup()~~~')

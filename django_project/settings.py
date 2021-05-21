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
import dj_database_url
from datetime import datetime, timedelta
from django.template import loader



# ~~~ PROD SETTINGS ~~~
# DATABASE_URL = os.environ['DATABASE_URL']
# DEBUG = 'False'
# ADMINS = [('tom', 't.alain@live.ca')] # send email if an exception is thrown

# ~~~ TEST SETTINGS ~~~
# DATABASE_URL = os.environ['TEST_DATABASE_URL']
# DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}
# DATABASES['default'] = dj_database_url.config()


DATABASE_URL = os.environ['DATABASE_URL']


# print('DATABASE_URL top: ' + DATABASE_URL) #TODO: REMOVE!!!!!
DEBUG = 'True'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# TODO: CONFIRM I DIDN'T BREAK ANYTHING AGAIN
# DATABASES = { # Use this to use local test DB # todo: prod doesn't have a access to django_session...
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db-test.sqlite3'),
#         #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#         'OPTIONS': {
#             'HOST': DATABASE_URL
#         }
#     }
# }





print('~~~At top of settings~~~ ')

SECRET_KEY = 'exhlfdat&vfum(-34*c2uroi(($ww(yo$9pv98=e6p^gl(-eoj' #todo: test removing this in own deployment

ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1']

mimetypes.add_type("text/css", ".css", True)

WSGI_APPLICATION = 'django_project.wsgi.application'
ASGI_APPLICATION = 'django_project.routing.application' # older version of django: 'django_project.routing.application'

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
    'axes', # https://django-axes.readthedocs.io/en/latest/2_installation.html
]

DJANGO_SETTINGS_MODULE = 'django_project.settings'
AUTH_USER_MODEL = 'users.MyUser'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware', # If you do not want Axes to override the authentication response you can skip
                                      # installing the middleware and use your own views.
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend', # AxesBackend should be the first backend in the AUTHENTICATION_BACKENDS list.
    'django.contrib.auth.backends.ModelBackend', # Django ModelBackend is the default authentication backend.
]
AXES_FAILURE_LIMIT = 5 # After this many failed login attempts, user is locked out
AXES_COOLOFF_TIME = timedelta(minutes=5) # unlock account after this many min from last failed attempt
AXES_LOCKOUT_URL = 'account/locked/' # Redirect to here if account is locked from failed login attempts

IS_PROD = os.environ['IS_PROD']
if IS_PROD is not None and IS_PROD == 'True':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') # Force https in prod
    SECURE_SSL_REDIRECT = True
    # DEBUG = 'False' #todo: uncomment
    ADMINS = [('Tom', 't.alain@live.ca')]  # send email if an exception is thrown

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
EMAIL_HOST_USER = os.environ.get('EMAIL_USER') # Google email username
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS') # Google email pass

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

print('~~~before heroku.locals()~~~')
django_heroku.settings(locals()) # todo: USED TO RUN LOCALHOST WITH DATABASE_URL (and other env settings)


CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')], #TODO: CONFIRM REDIS_URL WON'T FIRE CHATS TO PROD
        },
    },
}


DATA_UPLOAD_MAX_NUMBER_FIELDS = 4000
#django.setup() #todo maybe need... CAUSES ImportError: cannot import name 'User'
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
)





# ~~~NOT IN VERY-ACADEMY OR JUSTCHAT:~~~

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


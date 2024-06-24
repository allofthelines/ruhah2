'''
SHOULD WORK FOR
*LOCAL/DEVELOPMENT*
AND
*HEROKU/PRODUCTION* terminal: heroku config

terminal: heroku config
des
'''

import os
from pathlib import Path
import dj_database_url # postgres
from decouple import config, Csv # gia local/development mode
import django_heroku

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY') # inside .env file *1*(p%w5&n^zm=g3v0wb^kj1d9qzqm)f-pl#^o(izb6sp_z^fc
ENVIRONMENT = config('ENVIRONMENT', default='development')
DEBUG = config('DEBUG', default=True, cast=bool)
DOMAIN_NAME = config('DOMAIN_NAME', default='http://localhost:8000')

print('AT SETTINGS ENVIRONMENT IS', ENVIRONMENT)

# CELERY DEN DOULEVEI IDK GIATI
# TO EVALA GIA NA KATHARIZEI ITEMUSERCART KATHE 6 WRES
CELERY_ENABLED = config('CELERY_ENABLED', default='True', cast=bool)

# CELERY settings
if CELERY_ENABLED:
    CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
    CELERY_BEAT_SCHEDULE = {
        'clear_user_item_cart': {
            'task': 'accounts.tasks.clear_user_item_cart',
            'schedule': 21600.0,  # 6 hours in seconds
        },
    }
    CELERY_TIMEZONE = 'UTC'
else:
    CELERY_BROKER_URL = None
    CELERY_RESULT_BACKEND = None


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'fumio.xyz',
    'www.fumio.xyz',
    'ruhah.com',
    'www.ruhah.com',
    'fumio-c90be99ba1a3.herokuapp.com'
]

# IMPORTANT GIA STRIPE WEBHOOK
CSRF_TRUSTED_ORIGINS = [
    'https://sawfly-resolved-chimp.ngrok-free.app',
    'https://fumio.xyz',
    'https://www.fumio.xyz',
    'https://ruhah.com',
    'https://www.ruhah.com'
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'core.apps.CoreConfig', # app
    'box.apps.BoxConfig',  # app
    'accounts.apps.AccountsConfig',  # app
    'studio.apps.StudioConfig',  # app
    'pwa',
]

if DEBUG:
    INSTALLED_APPS += ["django_extensions"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ruhah.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ruhah.wsgi.application"







# DATABASE
# DATABASE
# DATABASE
print(f"Environment: {ENVIRONMENT}")

if ENVIRONMENT == 'production':
    DATABASES = {
        'default': dj_database_url.config(default=config('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='ruhahlocal'),
            'USER': config('DB_USER', default='arislocal'),
            'PASSWORD': config('DB_PASSWORD', default='passlocal'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }




# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True










# STATIC FILES (CSS, JavaScript, Images) + MEDIA FILES
# STATIC FILES (CSS, JavaScript, Images) + MEDIA FILES
# STATIC FILES (CSS, JavaScript, Images) + MEDIA FILES
# DEFAULT ENVIRONMENT == 'production'
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = None

STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage' # statics aws
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage' # media aws
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/' # uploaded by users

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'core/static'),
    ]

if ENVIRONMENT == 'development':
    # STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    # MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    # STATIC_URL = '/static/'
    # MEDIA_URL = '/media/'

    # mallon gia thn entolh collectstatic sto terminal
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'core/static'),
    ]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# TROUBLESHOOTING SVHSE ME
if ENVIRONMENT == 'development':
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'core/static'),
    ]
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')











# EMAIL SETTINGS
# EMAIL SETTINGS
# EMAIL SETTINGS
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'fumioxyz1@gmail.com'
EMAIL_HOST_PASSWORD = 'gcxtfsvznyycqowj'
DEFAULT_FROM_EMAIL = 'fumioxyz1@gmail.com'

# Ensure this is set to your production domain
if os.getenv('DJANGO_ENV') == 'production':
    # AFTO STELNEI TA EMAIL GIA SIGNUP CONFIRMATION
    EMAIL_DOMAIN = 'ruhah.com'
    EMAIL_PROTOCOL = 'https'
    SECURE_SSL_REDIRECT = True  # Redirect all HTTP requests to HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
else:
    EMAIL_DOMAIN = 'localhost:8000'
    EMAIL_PROTOCOL = 'http'

AUTH_USER_MODEL = 'accounts.CustomUser'






# PWA SETTINGS
# PWA SETTINGS
# PWA SETTINGS
PWA_APP_NAME = 'Ruhah'
PWA_APP_DESCRIPTION = "My Progressive Web App"
PWA_APP_THEME_COLOR = '#000000'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'any'
PWA_APP_START_URL = '/'
PWA_APP_ICONS = [
    {
        'src': '/static/images/icons/icon-72x72.png',
        'sizes': '72x72',
        'type': 'image/png'
    },
    {
        'src': '/static/images/icons/icon-96x96.png',
        'sizes': '96x96',
        'type': 'image/png'
    },
    {
        'src': '/static/images/icons/icon-128x128.png',
        'sizes': '128x128',
        'type': 'image/png'
    },
    {
        'src': '/static/images/icons/icon-144x144.png',
        'sizes': '144x144',
        'type': 'image/png'
    },
    {
        'src': '/static/images/icons/icon-152x152.png',
        'sizes': '152x152',
        'type': 'image/png'
    },
    {
        'src': '/static/images/icons/icon-192x192.png',
        'sizes': '192x192',
        'type': 'image/png'
    },
    {
        'src': '/static/images/icons/icon-384x384.png',
        'sizes': '384x384',
        'type': 'image/png'
    },
    {
        'src': '/static/images/icons/icon-512x512.png',
        'sizes': '512x512',
        'type': 'image/png'
    }
]

# STRIPE_SECRET_KEY = "sk_test_51HjtkWHCAjs916uo0avrWzOy7rb2tImrjRVgFKdWeXye6zFbn6sZrQafC2QTkpcsaGWPMgiTfIqigXA5lCFfDOFV00gJ5e6ekt"







# SHOPIFY
# SHOPIFY
# SHOPIFY
SHOPIFY_API_KEY_DEV = os.getenv('SHOPIFY_API_KEY_DEV')
SHOPIFY_API_SECRET_DEV = os.getenv('SHOPIFY_API_SECRET_DEV')
SHOPIFY_ACCESS_TOKEN_DEV = os.getenv('SHOPIFY_ACCESS_TOKEN_DEV')









# Activate Django-Heroku
# Activate Django-Heroku
# Activate Django-Heroku
if ENVIRONMENT == 'production':
    import django_heroku
    django_heroku.settings(locals())








'''
# tha borousa na ta valw etsi edw
# ta evala se heroku san environment variables
# sto terminal mou heroku config:set AWS_ACCESS_KEY_ID=AKIA3FLD37VQC5XLDFVV (5 fores)

heroku config:set AWS_ACCESS_KEY_ID=AKIA3FLD37VQC5XLDFVV
heroku config:set AWS_SECRET_ACCESS_KEY=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
heroku config:set AWS_S3_REGION_NAME=eu-north-1
heroku config:set AWS_STORAGE_BUCKET_NAME=ruhahbucket
heroku config:set AWS_S3_CUSTOM_DOMAIN=ruhahbucket.s3.amazonaws.com
heroku config:set DATABASE_URL=postgres://u2m4eitidqus9h:pee586005c3b1480311c39e8ae5fc8a73c73c3cc3a761f88757f6d6edea43b6f2@c8lj070d5ubs83.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/dce2g9f2qaunuh

heroku config

# AWS S3 settings
AWS_ACCESS_KEY_ID = 'AKIA3FLD37VQC5XLDFVV'
AWS_SECRET_ACCESS_KEY = '+UrGJhTOKYzqQR6FmtCWHxIk9AN7UESnno30rVB6'
AWS_STORAGE_BUCKET_NAME = 'ruhahbucket'
AWS_S3_REGION_NAME = 'eu-north-1'  # e.g., us-west-1
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = None
'''




"""LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
"""
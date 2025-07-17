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
    'ruhah.com',
    'www.ruhah.com',
    'fumio-c90be99ba1a3.herokuapp.com',
    'ruhah2-d3d177545264.herokuapp.com'
]

# IMPORTANT GIA STRIPE WEBHOOK
CSRF_TRUSTED_ORIGINS = [
    'https://sawfly-resolved-chimp.ngrok-free.app',
    'https://ruhah.com',
    'https://www.ruhah.com',
    'https://ruhah2-d3d177545264.herokuapp.com'
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
    # 'chatai.apps.ChataiConfig', #app
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
# The psql "version mismatch" warning is okay (it just means your client is v16, server is v17).
# did it because pgvector local only works for v17, not v16. but my dump heroku is v16
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
            'PASSWORD': config('DB_PASSWORD', default=''),
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
# AWS_DEFAULT_ACL = None
# TO EKANA COMMENT OUT LOGW TOU PROVLHMATOS ME STATIC
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False

STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage' # statics aws
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage' # media aws
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/' # uploaded by users

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'core/static/core'),
    ]

# In settings.py - development section only
if ENVIRONMENT == 'development':
    # Static files
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'core/static/core'),  # Your exact path
    ]
    # STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_dev')  den kserw giati yparxei mallon gia deploy AN DEN yphrxe s3

    # Media files
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

    # Disable AWS completely for development
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# TROUBLESHOOTING SVHSE Me
'''
if ENVIRONMENT == 'development':
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'core/static/core'),
    ]
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
'''











# EMAIL SETTINGS
# EMAIL SETTINGS
# EMAIL SETTINGS
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.privateemail.com' # ths namecheap
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'contact@ruhah.com'
EMAIL_HOST_PASSWORD = 'cocococo00'
DEFAULT_FROM_EMAIL = 'RUHAH <contact@ruhah.com>'

# Ensure this is set to your production domain
# if os.getenv('DJANGO_ENV') == 'production':
if os.environ.get('ENVIRONMENT') == 'production':
    # AFTO STELNEI TA EMAIL GIA SIGNUP CONFIRMATION
    EMAIL_DOMAIN = 'ruhah.com'
    EMAIL_PROTOCOL = 'https'
    SECURE_SSL_REDIRECT = True  # Redirect all HTTP requests to HTTPS
    PREPEND_WWW = True  # Adds www prefix ALLA xalaei to PWA (vazei bares panw katw)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_DOMAIN = '.ruhah.com'  # + VGAZEI TIS MPARES STO PWA OTAN WWW ENABLED
    CSRF_COOKIE_DOMAIN = '.ruhah.com' # + VGAZEI TIS MPARES STO PWA OTAN WWW ENABLED
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




# API KOLORS MODEL VIRTUAL TRY-ON
# API KOLORS MODEL VIRTUAL TRY-ONAdd commentMore actions
KOLORS_API_KEY = 'your_api_key_here'
KOLORS_API_SECRET = 'your_api_secret_here'
KOLORS_API_URL = 'https://kolors-model.api/tryon'  # Example endpoint URL

# GOOGLE API KEY
# GEMINI MILTIMODAL
# den prepei na einai mazi me vertex ai
# giafto to exw vgalei apo heroku config vars
GOOGLE_API_KEY="AIzaSyABrLYaoB4yDJdDEKBjwmJ3PYsi17Wkhks"



# VERTEX API
# VERTEX API
# Path to the Vertex AI service account JSON (from env)
# to evala kai sto heroku san variable
# meta, to file, einai ena oloklhro json file sto root dipla sto requirements.txt
# GOOGLE_VERTEX_SERVICE_ACCOUNT_FILE_PATH = os.environ.get("GOOGLE_VERTEX_SERVICE_ACCOUNT_FILE")







INVITE_CODE_REQUIRED = True


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
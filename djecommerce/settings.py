import os


# Initialise environment variables
# ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')


DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '-05sgp9!deq=q1nltm@^^2cc+v29i(tyybv3v2t77qi66czazj'
ALLOWED_HOSTS = ['164.92.189.162', '127.0.0.1', 'ecom.tovborg.live', 'tovborg.live']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    'django_countries',
    'paypal.standard.ipn',
    'sequences.apps.SequencesConfig',
    'sslserver',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'djecommerce.urls'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static_files')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT= os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'

PAYPAL_CLIENT_ID = "AQie0MKam6S2eIHkiYZTtoNxIJlNdVcD7pJN2aCp5wW-IRurKrBhsWDZ1Jmgnq_aNfyBCzg4FdS9uG5l"
PAYPAL_SECRET_ID = "ECmL-BwSGdtgNmgebInz_RQ8TPUdnyxIdFJE9xjg2W6iHldKwql7bW4WrYnrB9UMVn_Ubgnvo5L3zzTf"

# if DEBUG:
#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.sqlite3",
#             "NAME": os.path.join(BASE_DIR, 'db.sqlite3')
#         }
#     }
# else:
if DEBUG is False:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'ecomdb',
            'USER': 'ecomdb_admin',
            'PASSWORD': 'Rasmus2010',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, 'db.sqlite3')
        }
    }


SITE_ID = 1
LOGIN_REDIRECT_URL = '/'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

STRIPE_PUBLIC_KEY = 'pk_test_51Kw5nlHaBBAjc5DS2FyREpZSQ6BhFoF2pc9Oxak3wjZnf1CGS0see6HHcggu8dbovqdzVo6xol16oDsyfDtlmDKl00dDIiLKA5'
STRIPE_PRIVATE_KEY = 'sk_test_51Kw5nlHaBBAjc5DSo1oyLsNtPTw2rFaUU7PdSqaiX4IDryTAqLcVZ4X1utQT6hwCL8urhiQaU18arBedsmAvk2QH00jxEvRxw0'
STRIPE_ENDPOINT_SECRET = 'whsec_f6a66c60a06a9984ca9dd55378ea6eb88a65bef34040eba8921378e087ef2682'

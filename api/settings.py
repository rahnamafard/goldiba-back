import os
from datetime import timedelta
from corsheaders.defaults import default_headers

# remove in production mode
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# BASE_DIR = '/'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'yji4pd3+2tu*1@m+$)h*^e+_!ub^b90220o#tv1%vjih#vq5)&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',     # token authentication
    'corsheaders',                  # cors headers
    'core'                          # core app
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware', # Disabled Due to CORS Conflicts!!!
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'api.wsgi.application'

# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = False
USE_L10N = False
USE_TZ = False

STATIC_URL = '/static/'
STATIC_ROOT = '/static/'

# MEDIA_URL = 'http://135.181.168.71:8000/'  # online localhost
MEDIA_URL = '/'  # offline localhost
MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_URL)

DATA_UPLOAD_MAX_MEMORY_SIZE = 1024000

# Authentication Settings
AUTH_USER_MODEL = 'core.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}

# Log Settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
        'file': {
            'format': '%(levelname)-8s %(message)s\n         %(asctime)s --> %(name)s\n'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': 'debug.log'
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        }
    }
}

# kavenegar
# sms_api_key = '6E52696C5047566E49714E6973446E5847747676316648664C7579797043434E2B6C5033365978302F72513D' # arahnamafard@yahoo.com
sms_api_key = '6369352B674A66434345645633586A70352F4674414A61347565557142424A6A6A313053456B76413030673D'  # nourifatemeh441@gmail.com
sms_api_url = "https://api.kavenegar.com/v1/{}/verify/lookup.json".format(sms_api_key)

# zibal
zibal_request_url = 'https://gateway.zibal.ir/v1/request'  # post
zibal_verify_url = 'https://gateway.zibal.ir/v1/verify'  # post
merchant_key = '5f81b70318f93473c1e674c9'
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Detect environment based on an environment variable
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

# Secret key from environment
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# Allowed hosts
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'turnusnumero13.com', 'www.turnusnumero13.com']

# Email settings
if DEBUG:
    # Local development: emails printed to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Production: real emails sent via Gmail (with App Password)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Login/logout redirects
LOGIN_REDIRECT_URL = "/schedule/"
LOGOUT_REDIRECT_URL = "/login/"
LOGIN_URL = "/login/"

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

# Database settings
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': '3306',
        }
    }

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django_extensions",
    'shifts',
    'rest_framework',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URLs and templates
ROOT_URLCONF = 'shiftbooking.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "shifts/templates"],
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

WSGI_APPLICATION = 'shiftbooking.wsgi.application'

# Static files
STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

# Time zone and internationalization
LANGUAGE_CODE = 'nb'
USE_I18N = True
TIME_ZONE = 'UTC'
USE_TZ = True

# Password validators
AUTH_PASSWORD_VALIDATORS = []

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

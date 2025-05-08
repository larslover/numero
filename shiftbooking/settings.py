import os
from pathlib import Path
DEBUG = False


# Get the base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Check if the environment is production or local
IS_PRODUCTION = not DEBUG

# Email settings for local and production
if IS_PRODUCTION:
    # Use a real email backend in production
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.your-email-provider.com'  # Replace with your email provider's SMTP host
    EMAIL_PORT = 587  # Usually 587 for TLS or 465 for SSL
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'your-email@example.com'  # Your email username
    EMAIL_HOST_PASSWORD = 'your-email-password'  # Your email password
else:
    # Use the console email backend for local development (prints to console)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Other settings
LOGIN_REDIRECT_URL = "/schedule/"
LOGOUT_REDIRECT_URL = "/login/"
LOGIN_URL = "/login/"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'turnusnumero13.com', 'www.turnusnumero13.com']


SECRET_KEY = 'django-insecure-s4+)prj7&)q=z-k@p800%dz)$7orix-hdx-uewpfdm+re9puh3'


if DEBUG:
    # Local development: use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Production (PythonAnywhere): use MySQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'LarsLover$numero13',
            'USER': 'LarsLover',
            'PASSWORD': 'Simplicity',
            'HOST': 'LarsLover.mysql.pythonanywhere-services.com',
            'PORT': '3306',
        }
    }

# Other Django settings
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

# Static files settings
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'shifts/static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Time zone and internationalization settings
LANGUAGE_CODE = 'nb'
USE_I18N = True
TIME_ZONE = 'UTC'
USE_TZ = True

# Password validators
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

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

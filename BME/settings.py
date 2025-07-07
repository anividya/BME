from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-qz7d=-etqe*=3#h0-1xt$%vk6jo475x052yym%=p2j%opa##f('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'BMEAPP',
    'bootstrap5',
    'crispy_forms',
    'django_filters',
    'bootstrapform',
    'widget_tweaks',
    'rest_framework_simplejwt',
    'django_celery_beat',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'fcm_django',
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY": "BHKOMJK8uhNBahwWI7UYdW4r8Vd8N4mA4-FrIJ_wKVgb6p6d8SclUq1zISIKG9OhA_R9T6vl8XxqeARwSBS9bbE"
}

CORS_ALLOW_ALL_ORIGINS = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BME.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'BMEAPP/templates')],
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

#SECURE_SSL_REDIRECT = True
#SECURE_HSTS_SECONDS = 3600
#SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#SECURE_HSTS_PRELOAD = True
#CSRF_COOKIE_SECURE = True
#SESSION_COOKIE_SECURE = True


CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
CELERY_BROKER_URL = 'amqp://guest:guest@127.0.0.1:5672//'
CELERY_RESULT_BACKEND = 'rpc://'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname}/{processName}/{name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'celery.log'),
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}


WSGI_APPLICATION = 'BME.wsgi.application'

CSRF_TRUSTED_ORIGINS = [
    'https://aneesh.tail25f251.ts.net',  # Replace with your Tailscale URL
]



# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

#DATABASES = {
    #'default': {
      #  'ENGINE': 'django.db.backends.sqlite3',
      #  'NAME': BASE_DIR / 'db.sqlite3',
   # }
#}

from dotenv import load_dotenv
load_dotenv()  # Load .env file

DATABASES = {
    'default': {
       'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bmedb',
        'USER': 'postgres',
        'PASSWORD': 'Anividya@123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


CRON_CLASSES = [
    "BMEAPP.cron.UpdatePmStatJob",
]


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

#TIME_ZONE = 'Asia/Kolkata'
TIME_ZONE = 'Asia/Dubai'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
# For production
STATIC_ROOT = BASE_DIR / "staticfiles"

# settings.py

MEDIA_URL = '/media/'  # URL prefix for media files
MEDIA_ROOT = BASE_DIR / 'media'  # Directory to store uploaded media files



# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

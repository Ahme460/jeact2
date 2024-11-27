"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import timedelta

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8^h!6a%l!e%dc6!%ef%ooxlo-m14x@2&&n6j#@d-a7-=@c&1#0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "unfold",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app1',
    'django_filters',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_celery_beat',
    'drf_yasg',
    'corsheaders',
    'django.contrib.sites',
     'ckeditor',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
#CORS_ALLOW_CREDENTIALS = True

# السماح بالطرق المحددة إذا لزم الأمر
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

CORS_ALLOWED_ORIGINS = [
    'https://bantyaga.vercel.app',
]

# السماح برؤوس محددة إذا لزم الأمر
#CORS_ALLOW_HEADERS = [
#     'accept',
#     'accept-encoding',
#     'authorization',
#     'content-type',
#     'dnt',
#     'origin',
#     'user-agent',
#     'x-csrftoken',
#     'x-requested-with',
# ]



ROOT_URLCONF = 'project.urls'

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

WSGI_APPLICATION = 'project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bentage',
        'USER': 'bentageuser',
        'PASSWORD': 'securepassword',
        'HOST': 'localhost',  # أو '127.0.0.1'
        'PORT': '',  # استخدم القيمة الافتراضية
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'app1.Customer_user'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=600),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'  # استخدام قاعدة البيانات كخلفية لحفظ نتائج العمليات

# Swagger Settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        }
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, "static")

# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# DEFAULT_FROM_EMAIL = "bentagwy2121@gmail.com"
# EMAIL_PORT = 587
# EMAIL_HOST_USER = "bentagwy2121@gmail.com"
# EMAIL_HOST_PASSWORD = "llux mtlk fvot yekd" 
# FRONTEND_URL=''
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


EMAIL_USE_SSL = True 
EMAIL_HOST = 'smtp.hostinger.com'
DEFAULT_FROM_EMAIL = "info@bantayga.wtf"
EMAIL_PORT = 465  
EMAIL_HOST_USER = "info@bantayga.wtf"
EMAIL_HOST_PASSWORD = "Bantayga.wtf1" 
FRONTEND_URL='https://bantayga.wtf'
















# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
SITE_ID = 1


UNFOLD ={
    
    'extra_css': [
        '/static/unfold/custom_admin.css',  # مسار ملف CSS المخصص
    ],

    
        "SITE_TITLE": "bantayga",
    "SITE_HEADER": "bantayga_big_Store",
     "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
            },
        },
    },
     
     
      "STYLES": [
        lambda request: static("css/style.css"),
    ],
    "SCRIPTS": [
        lambda request: static("js/script.js"),
    ],
    
}



CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 700,
        'width': '100%',
    },
}
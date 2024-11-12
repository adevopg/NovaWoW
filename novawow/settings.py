"""
Django settings for novawow project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-os9f6#@x_5*sfv2g6vyj*31$964_s%7(%&x0+m)crrbj^=0wus'

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
    'home',
    'django_ckeditor_5',
]

# Configuración para AC SOAP
AC_SOAP_URL = "http://127.0.0.1:2079"
AC_SOAP_USER = "AC_SOAP"
AC_SOAP_PASSWORD = "Ladyamy89"
AC_SOAP_URN = "urn:AC"

 
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|', 'bold', 'italic', 'underline', 'link', 'bulletedList', 'numberedList', 
            '|', 'alignment', 'outdent', 'indent', '|', 'blockQuote', 'codeBlock', 
            'insertTable', 'mediaEmbed', '|', 'undo', 'redo'
        ],
        'height': '400px',
        'width': '100%',
        'language': 'es',
        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells'
            ]
        },
        'mediaEmbed': {
            'previewsInData': True
        },
    }
}


CSP_FRAME_SRC = [
    "https://www.youtube.com",
    "https://www.youtube.com/embed/",
]
CSP_DEFAULT_SRC = ["'self'", "https://www.youtube.com"]

X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_CONTENT_TYPE_NOSNIFF = False



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'novawow.urls'

URL_PRINCIPAL = ''

# Nombre del servidor
NOMBRE_SERVIDOR = "Nova WoW"

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'novawow_session'
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 3600  # 1 hora

# Año actual
from datetime import datetime
ANIO_ACTUAL = datetime.now().year

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'home.context_processors.url_principal',
                'home.context_processors.configuracion_global',
                'home.context_processors.get_server_info',
            ],
        },
    },
]


WSGI_APPLICATION = 'novawow.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django_wow',
        'USER': 'Inna',
        'PASSWORD': '@dsJ210624@',
        'HOST': 'localhost',
        'PORT': '3306',
    },
    'acore_auth': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'acore_auth',
        'USER': 'Inna',
        'PASSWORD': '@dsJ210624@',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    
     'acore_characters': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'acore_characters',
        'USER': 'Inna',
        'PASSWORD': '@dsJ210624@',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
}


AC_LOGON = None

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGES = [
    ('es', 'Español'),
    # Agrega otros idiomas aquí si los necesitas
    # ('en', 'English'),
]

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

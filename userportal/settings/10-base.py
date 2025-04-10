"""
Django settings for userportal project.
"""

from pathlib import Path
from django.utils.translation import gettext_lazy as _
import os
import saml2
import saml2.saml
import logging.config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'changeme'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'djangosaml2',
    'csp',
    'watchman',

    'pages',
    'slurm',
    'notes',

    'jobstats',
    #'accountstats',
    #'cloudstats',
    # 'quotas',
    'top',
    #'usersummary',
    'nodes',

    'ccldap',

    # system modules
    'rest_framework',
    'rest_framework.authtoken',
    'bootstrap_pagination',
]

MIDDLEWARE = []

MIDDLEWARE += [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'djangosaml2.middleware.SamlSessionMiddleware',
    'csp.middleware.CSPMiddleware',
]

ROOT_URLCONF = 'userportal.urls'

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
                'django_settings_export.settings_export',
                'django.template.context_processors.request',
            ],
            'builtins': ['userportal.templatetags'],
        },
    },
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

WSGI_APPLICATION = 'userportal.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = [
    ('fr', _('French')),
    ('en', _('English')),
]

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

BASE_URL = '/'
STATIC_URL = '/static/'
STATIC_ROOT = '/opt/userportal/collected-static/'

AUTHENTICATION_BACKENDS = [
    'userportal.authentication.staffRemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
    'userportal.authentication.staffSaml2Backend',
]

LDAP_BASE_DN = 'dc=computecanada,dc=ca'

LOGIN_REDIRECT_URL = '/'

# Set to DEMO to True to enable demo mode with anonymized data
# This is partially done in javascript, so its only safe in a presentation in fullscreen
# The URLs still contains the real usernames
DEMO = False

SETTINGS_EXPORT = [
    'CLUSTER_NAME_TITLE',
    'FAVICON',
    'EXPORTER_INSTALLED',
    'INSTALLED_APPS',
    'EXTERNAL_LINKS',
    'OTHER_PORTALS',
    'BASE_URL',
    'DEMO',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 100,
}

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'")
CSP_IMG_SRC = ("'self'", "data:", 'object-arbutus.cloud.computecanada.ca')
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", 'cdn.jsdelivr.net', 'cdnjs.cloudflare.com', 'cdn.datatables.net')
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", 'cdn.jsdelivr.net', 'cdnjs.cloudflare.com', 'cdn.datatables.net', 'code.jquery.com', 'cdn.plot.ly')

"""
Django settings for rivers project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qcbjp($_@n6(6ko(uxy6y4f3co)31tl7kdaly8!s#bk0$3u6bb'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = (
    # plugin package, django suit and adminplus
    #'suit',
    'django_admin_bootstrapped',
    'adminplus',
    'widget_tweaks',

    # django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # base app
    'base',

    # tos import
    'tos_import',
    'tos_import.statement.statement_account',
    'tos_import.statement.statement_position',
    'tos_import.statement.statement_trade',

    # statistic
    'statistic.simple.stat_day',

    # position
    'position',

    # data
    'data',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'rivers.urls'

WSGI_APPLICATION = 'rivers.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
)

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'rivers_default',
        'USER': 'admin',
        'PASSWORD': 'qwer1234',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    },
    'quote': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'rivers_quote',
        'USER': 'admin',
        'PASSWORD': 'qwer1234',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    },
}
"""
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '__test__.db'),
    },
    'quote': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '__quote__.db'),
    },
"""

DATABASE_ROUTERS = ['rivers.router.DataRouter']

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

# TEST_RUNNER = None

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    'static',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,  'templates'),
)

DATE_FORMAT = 'Y-m-d'

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'fixtures'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '%s/debug.log' % BASE_DIR,
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '%s/debug.log' % BASE_DIR,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['file_debug'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'django': {
        'handlers': ['console'],
        'propagate': True,
        'level': 'INFO',
    },
}

# no cache for development stage
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# test using sqlite
if 'test' in sys.argv or 'test_coverage' in sys.argv:  # Covers regular testing and django-coverage
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
    DATABASES['default']['NAME'] = os.path.join(BASE_DIR, '__test__.db'),
    DATABASES['quote']['ENGINE'] = 'django.db.backends.sqlite3'
    DATABASES['quote']['NAME'] = os.path.join(BASE_DIR, '__quote__.db'),
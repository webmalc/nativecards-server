"""
Django settings for nativecards project.
"""

import datetime
import os

import raven
from kombu import Queue

try:
    from .settings_local import *
    from .settings_local import DEBUG
    import psycopg2
except ImportError:  # pragma: no cover
    # Fall back to psycopg2cffi
    from psycopg2cffi import compat
    compat.register()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'raven.contrib.django.raven_compat',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'debug_toolbar',
    'django_extensions',
    'reversion',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'ajax_select',
    'ordered_model',
    'rest_framework',
    'django_filters',
    'annoying',
    'ckeditor',
    'markdownx',

    # Nativecards apps
    'nativecards',
    'cards',
]

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'nativecards.middleware.DisableAdminI18nMiddleware',
    'nativecards.middleware.AuthenticationMiddlewareJWT',
    'nativecards.middleware.WhodidMiddleware',
    'reversion.middleware.RevisionMiddleware',
]

ROOT_URLCONF = 'nativecards.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'nativecards/templates'),
        ],
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

WSGI_APPLICATION = 'nativecards.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.\
UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', 'English'),
    ('ru', 'Russian'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'nativecards/static'),
    os.path.join(BASE_DIR, 'node_modules'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

FIXTURE_DIRS = (os.path.join(BASE_DIR, 'fixtures'), )
LOCALE_PATHS = (
    os.path.join(os.path.dirname(__file__), "locale"),
    os.path.join(os.path.dirname(__file__), "app_locale"),
)

EMAIL_SUBJECT_PREFIX = '[Nativecards]: '
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240
INTERNAL_IPS = ['127.0.0.1']

# Logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],  # , 'watchtower'],
    },
    'formatters': {
        'verbose': {
            'format':
            "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt':
            "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/nativecards.log',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose'
        },
        'sentry': {
            'level': 'ERROR',
            'class':
            'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'filters': ['require_debug_false'],
            'tags': {
                'custom-tag': 'x'
            },
        },
        # 'watchtower': {
        #     'level': 'ERROR',
        #     'filters': ['require_debug_false'],
        #     'class': 'watchtower.CloudWatchLogHandler',
        #     'formatter': 'simple'
        # },
    },
    'loggers': {
        'nativecards': {
            'handlers': ['file', 'mail_admins', 'sentry'],
            'level': 'DEBUG',
        },
    }
}

# Two factor auth
LOGIN_URL = 'two_factor:login'
LOGOUT_URL = "admin:logout"
LOGIN_REDIRECT_URL = 'admin:index'

# Celery
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_ALWAYS_EAGER = False
CELERY_APP = 'nativecards'
CELERY_QUEUES = (
    Queue('default'),
    Queue('priority_high'),
)
CELERY_DEFAULT_QUEUE = 'default'
CELERYD_TASK_SOFT_TIME_LIMIT = 60 * 5
# CELERYBEAT_SCHEDULE = {}

# Django restframework
REST_FRAMEWORK = {
    'DEFAULT_VERSION':
    '1.0',
    'DEFAULT_VERSIONING_CLASS':
    'rest_framework.versioning.AcceptHeaderVersioning',
    'DEFAULT_PAGINATION_CLASS':
    'nativecards.pagination.StandardPagination',
    'DEFAULT_PERMISSION_CLASSES': [
        'nativecards.permissions.DjangoModelPermissionsGet',
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

if not DEBUG:  # pragma: no cover
    # Sentry raven
    RAVEN_CONFIG = {
        'dsn':
        'https://52126dbda9494c668b7b9dff7722c901:\
31b56314232c436fb812b98568a5f589@sentry.io/200649',
        'release':
        raven.fetch_git_sha(os.path.dirname(os.pardir)),
    }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 60 * 60 * 24 * 7,
        # 'LOCATION': 'unix:/tmp/memcached.sock',
    }
}

# DRM estensions
REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60 * 24 * 7,
    'DEFAULT_CACHE_ERRORS': False,
    'DEFAULT_USE_CACHE': 'default'
}

# Django REST framework JWT
JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),
}

# Ckeditor
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Basic',
    },
}

# Nativecards
NC_IMAGE_WIDTH = 150
NC_ATTEMPTS_TO_REMEMBER = 10
NC_CARDS_PER_LESSON = 10
NC_CARDS_TO_REPEAT = 5
NC_LESSON_LATEST_DAYS = 21

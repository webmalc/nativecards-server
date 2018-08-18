from .settings import *

LOGGING.pop('root', None)

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_BACKEND = 'memory'

ADMINS = (('admin', 'admin@example.com'), ('manager', 'manager@example.com'))

MANAGERS = ADMINS
TESTS = True

CORS_ORIGIN_ALLOW_ALL = True

DEBUG = False
TEMPLATE_DEBUG = False

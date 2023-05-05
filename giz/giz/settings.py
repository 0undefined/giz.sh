import os
from os.path import dirname, realpath, join

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = realpath(join(dirname(__file__), '..'))
APP_DIR = os.path.join(PROJECT_ROOT, 'app')

os.path.join(BASE_DIR, APP_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

try:
    SECRET_KEY = os.environ['SECRET_KEY']
except KeyError as e:
    raise RuntimeError("Could not find $SECRET_KEY in environment")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", not os.getenv("PROD", True))


DEFAULT_DOMAIN = 'giz.sh'
ALLOWED_HOSTS = [DEFAULT_DOMAIN, '127.0.0.1', '70.34.196.53']


if DEBUG:
    import socket  # only if you haven't already imported this
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

    ALLOWED_HOSTS.append('localhost')

# Application definition

INSTALLED_APPS = [
    'users',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    # Apps
    'index',
    'gitolite',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
else:
    #SECURE_SSL_REDIRECT=True
    SESSION_COOKIE_SECURE=True
    CSRF_COOKIE_SECURE=True

CSRF_TRUSTED_ORIGINS = [
    'http://' + DEFAULT_DOMAIN, 'https://' + DEFAULT_DOMAIN,
    'http://www.' + DEFAULT_DOMAIN, 'https://www.' + DEFAULT_DOMAIN,
    'http://127.0.0.1', 'http://70.34.196.53'
]

ROOT_URLCONF = 'giz.urls'

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

WSGI_APPLICATION = 'giz.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {}
if DEBUG:
    CACHES['default'] = {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
else:
    CACHES['default'] = {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379",
    }


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
AUTH_USER_MODEL = "users.user"

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

# NB: These are named url patterns, but can also be just urls.
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'index'

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_URL = '/static/'
STATIC_ROOT = '/usr/share/giz/static'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

SHARE_DIR = '/usr/share'
# only used to communicate with gitolite locally
GITOLITE_ADMIN_PATH = os.getenv("GITOLITE_ADMIN_PATH", os.path.join(SHARE_DIR, 'gitolite-admin'))
GITOLITE_GIT_PATH = os.getenv("GITOLITE_ADMIN_PATH", os.path.join(SHARE_DIR, 'git', 'repositories'))
GITOLITE_HOST = os.getenv("GITOLITE_HOST", 'gitolite')
GITOLITE_PORT = int(os.getenv("GITOLITE_PORT", 22))
GITOLITE_KEY = os.getenv("GITOLITE_KEY", os.environ['HOME'] + "/.ssh/id_rsa")

# Used to calculate remote url
GITOLITE_REMOTE = 'localhost' if DEBUG else DEFAULT_DOMAIN

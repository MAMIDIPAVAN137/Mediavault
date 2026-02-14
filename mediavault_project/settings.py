import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-h_*8r+-+31iz*km4e_t3kgip#$q^*&mac3dd@@)&=&ltbvjx)g')

DEBUG = True

# In production, ALLOWED_HOSTS should be a list of domain names, e.g., ['my-app.onrender.com']
# We'll default to '*' if not provided for convenience, but it's better to be specific.
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# --- APPLICATION DEFINITION ---
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
    'media',
    'social',
    'stats',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mediavault_project.urls'

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
                'social.context_processors.notifications_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'mediavault_project.wsgi.application'
ASGI_APPLICATION = 'mediavault_project.asgi.application'

# --- DATABASE ---
# Uses Render's DATABASE_URL or fallbacks to local SQLite
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:////{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}

# --- AUTHENTICATION ---
AUTH_USER_MODEL = 'core.User'
LOGIN_REDIRECT_URL = 'profile'
LOGOUT_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = [
    'core.backends.EmailOrPhoneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = []

# --- STATIC & MEDIA FILES ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise Storage (Compressed & Manifest for high performance)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media_root'

# --- REST FRAMEWORK ---
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ]
}

# --- PRODUCTION SECURITY SETTINGS ---
CSRF_TRUSTED_ORIGINS = [
    "https://mediavault-g49l.onrender.com"
]

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# For HTTPS (uncomment when SSL/TLS is enabled on Render)
# SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- CHANNELS ---
if os.environ.get('REDIS_URL'):
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [os.environ.get('REDIS_URL')],
            },
        },
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

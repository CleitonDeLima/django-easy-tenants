import tempfile
from pathlib import Path

import environ

BASE_DIR = Path(__file__).parent

env = environ.Env(
    DATABASE=(str, 'sqlite')
)

envfile = BASE_DIR / 'configs' / f'{env("DATABASE")}.env'
environ.Env.read_env(str(envfile))

SECRET_KEY = 'any-key'
ROOT_URLCONF = 'tests.urls'

DATABASES = {
    'default': env.db()
}

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'easy_tenants.middleware.DefaultTenantMiddleware',
]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'easy_tenants',
    'tests',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
    },
]

EASY_TENANTS_MODEL = 'tests.StoreTenant'
EASY_TENANTS_REDIRECT_URL = 'store-list'
EASY_TENANTS_SUCCESS_URL = 'home'

MEDIA_ROOT = tempfile.gettempdir()
MEDIA_URL = '/media/'

STATIC_URL = '/static/'

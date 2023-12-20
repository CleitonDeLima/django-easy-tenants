import tempfile
from pathlib import Path

import environ

BASE_DIR = Path(__file__).parent

env = environ.Env(DATABASE=(str, "sqlite"))

if env("DATABASE") == "postgres":
    db_url = "postgres://postgres:postgres@localhost:5432/easy_tenants"
else:
    db_url = "sqlite://:memory:"


SECRET_KEY = "any-key"
ROOT_URLCONF = "tests.urls"

DATABASES = {"default": environ.Env.db_url_config(db_url)}

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "easy_tenants",
    "tests",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
    },
]

MEDIA_ROOT = tempfile.gettempdir()
MEDIA_URL = "/media/"

STATIC_URL = "/static/"

EASY_TENANTS_TENANT_FIELD = "store"
EASY_TENANTS_TENANT_MODEL = "tests.StoreTenant"

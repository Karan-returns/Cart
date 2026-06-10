from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    DISCOUNT_EVERY_N_ORDERS=(int, 3),
    DISCOUNT_PERCENT=(int, 10),
    DISCOUNT_CODE_PREFIX=(str, "SAVE"),
    ADMIN_API_KEY=(str, "dev-admin-key"),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="django-insecure-dev-only-key")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "rest_framework",
    "store",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# Minimal DB config for Django test runner; app uses in-memory repositories.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
    "EXCEPTION_HANDLER": "store.exceptions.custom_exception_handler",
}

DISCOUNT_EVERY_N_ORDERS = env("DISCOUNT_EVERY_N_ORDERS")
DISCOUNT_PERCENT = env("DISCOUNT_PERCENT")
DISCOUNT_CODE_PREFIX = env("DISCOUNT_CODE_PREFIX")
ADMIN_API_KEY = env("ADMIN_API_KEY")

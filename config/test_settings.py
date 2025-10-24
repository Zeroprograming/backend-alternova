# Configuración de Django para Testing - Simplificada

import os

# Configuración básica
DEBUG = True
TESTING = True
SECRET_KEY = "test-secret-key-for-testing-only"

# Base de datos de testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Cache de testing
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Configuración de archivos estáticos
STATIC_URL = "/static/"
STATIC_ROOT = "staticfiles"

# Configuración de media
MEDIA_URL = "/media/"
MEDIA_ROOT = "media"

# Configuración de allowed hosts
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# Configuración de logging para testing
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "common": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}

# Configuración de email para testing
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Middleware básico
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Aplicaciones instaladas básicas
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "common",
    "users",
    "notifications",
    "subjects",
    "reports",  # Added for reports app testing
]

# Configuración de REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# Configuración de archivos estáticos
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Configuración de media
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_media")

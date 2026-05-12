"""
Django settings for medimap_project project.
"""

from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------
# SECURITY
# -------------------------------------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-&-#4%f5q@m#)4$#w+*o%*&ik3li$6e6lc@b)v)zkypin%z!!@x"
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost"
).split(",")

# -------------------------------------------------------
# APPLICATIONS
# -------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "clinics",
]

# -------------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -------------------------------------------------------
# URL / WSGI
# -------------------------------------------------------
ROOT_URLCONF = "medimap_project.urls"

WSGI_APPLICATION = "medimap_project.wsgi.application"

# -------------------------------------------------------
# TEMPLATES
# -------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# -------------------------------------------------------
# DATABASE - PostgreSQL (use DATABASE_URL for Render)
# -------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=f"postgres://postgres:pajarillo14@localhost:5432/medimap_db"
    )
}

# -------------------------------------------------------
# PASSWORD VALIDATION
# -------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------------------------
# LANGUAGE / TIME
# -------------------------------------------------------
LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Manila"

USE_I18N = True

USE_TZ = True

# -------------------------------------------------------
# STATIC FILES
# -------------------------------------------------------
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Collect static files in production
STATIC_ROOT = BASE_DIR / "staticfiles"

# -------------------------------------------------------
# DEFAULT PRIMARY KEY
# -------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------------------------------
# LOGIN / LOGOUT SETTINGS
# -------------------------------------------------------
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "admin_page"
LOGOUT_REDIRECT_URL = "login"

# -------------------------------------------------------
# RENDER / PRODUCTION SETTINGS
# -------------------------------------------------------
# Allow HTTPS redirect if needed
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "False") == "True"
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
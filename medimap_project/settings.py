"""
Django settings for medimap_project project (works locally and on Render)
"""

from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------- SECURITY ----------------
# SECRET_KEY: use environment variable in production, fallback for local dev
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-fallback-local-secret-key"
)

# DEBUG: True locally, False on Render
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

# ALLOWED_HOSTS: local defaults + environment variable for Render
ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost,medimap-clinic-locator.onrender.com"
).split(",")

# ---------------- APPLICATIONS ----------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "clinics",
]

# ---------------- MIDDLEWARE ----------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------------- URL / WSGI ----------------
ROOT_URLCONF = "medimap_project.urls"
WSGI_APPLICATION = "medimap_project.wsgi.application"

# ---------------- TEMPLATES ----------------
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

# ---------------- DATABASE ----------------
# Use local Postgres for development, DATABASE_URL for Render
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get(
            "DATABASE_URL",
            "postgres://postgres:pajarillo14@localhost:5432/medimap_db"
        )
    )
}

# ---------------- PASSWORD VALIDATION ----------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------- LANGUAGE / TIME ----------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Manila"
USE_I18N = True
USE_TZ = True

# ---------------- STATIC FILES ----------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ---------------- DEFAULT PRIMARY KEY ----------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------- LOGIN / LOGOUT ----------------
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "admin_page"
LOGOUT_REDIRECT_URL = "login"

# ---------------- PRODUCTION / RENDER SETTINGS ----------------
# HTTPS (optional)
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "False") == "True"
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
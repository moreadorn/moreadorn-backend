"""
Django settings for importexportmanage project.

Sensitive values (SECRET_KEY, database credentials) are loaded from a `.env`
file via python-decouple. See `.env.example` at the project root.
"""

from pathlib import Path
import dj_database_url
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent


# =====================================================================
# CORE
# =====================================================================
SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-a!$=%m!7i=9mg5+ag_s$j+q5e@n5ll+m*w)9l*yl#8%c8&($8c",
)
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())


# =====================================================================
# APPS
# =====================================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    # Local
    "moreadornexportapp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # must be high in the list
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "importexportmanage.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "importexportmanage.wsgi.application"


# =====================================================================
# DATABASE — PostgreSQL via single DATABASE_URL (parsed by dj-database-url)
# Format: postgresql://USER:PASSWORD@HOST:PORT/DB_NAME
# Manage the database itself through pgAdmin.
# =====================================================================
DATABASES = {
    "default": dj_database_url.config(
        default=config(
            "DATABASE_URL",
            default="postgresql://postgres:root@127.0.0.1:5432/moreadorn_db",
        ),
        conn_max_age=60,
        conn_health_checks=True,
    ),
}
DATABASES["default"].setdefault("OPTIONS", {})["client_encoding"] = "UTF8"


# =====================================================================
# AUTH
# =====================================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# =====================================================================
# I18N
# =====================================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True


# =====================================================================
# STATIC & MEDIA
# Images and videos uploaded via the admin panel are stored on the
# server's disk (MEDIA_ROOT) and served from MEDIA_URL — no object
# storage required, no base64 bloat in the database.
# =====================================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Upload limits — keep large enough for product images / short videos
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50 MB

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =====================================================================
# CORS — allow the React frontend (Vite dev server / deployed build)
# ---------------------------------------------------------------------
# Two ways to configure:
#   1. Whitelist via CORS_ALLOWED_ORIGINS env var (production-safe).
#   2. Toggle CORS_ALLOW_ALL=True in `.env` to bypass the whitelist
#      entirely while developing on multiple ports / IPs.
# =====================================================================
CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL", default=False, cast=bool)

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default=(
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:5174,"
        "http://127.0.0.1:5174,"
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    ),
    cast=Csv(),
)

# Allow any localhost / 127.0.0.1 port (handy when Vite hops to 5174/5175 etc.)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://localhost:\d+$",
    r"^http://127\.0\.0\.1:\d+$",
]

CORS_ALLOW_CREDENTIALS = True

# Methods the SPA actually uses.
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# Headers the SPA sends (Authorization is required for the token-auth
# admin flow; the rest are the standard CORS-safelist + content-type).
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# Cache the preflight response for an hour so OPTIONS doesn't run on
# every request.
CORS_PREFLIGHT_MAX_AGE = 60 * 60

# CSRF trusted origins — required by Django 4+ when the SPA POSTs over
# HTTPS or from a different origin. We mirror the CORS whitelist so
# both stay in sync with one .env variable.
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default=",".join(CORS_ALLOWED_ORIGINS),
    cast=Csv(),
)


# =====================================================================
# EMAIL — Gmail SMTP (credentials in .env)
# =====================================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("GMAIL_USERNAME", default="").strip("'\"")
EMAIL_HOST_PASSWORD = config("GMAIL_PASSWORD", default="").strip("'\"")
DEFAULT_FROM_EMAIL = f"Moreadorn <{EMAIL_HOST_USER}>"
EMAIL_TIMEOUT = 20

# Brand info available to email templates
SITE_NAME = "Moreadorn"
SITE_TAGLINE = "Global Trade Co."
SITE_URL = config("SITE_URL", default="http://localhost:5173")


# =====================================================================
# DJANGO REST FRAMEWORK
# =====================================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 9,
    # Browsable API is convenient locally but exposes a UI in production.
    # Keep both renderers in DEBUG, ship JSON-only when DEBUG is False.
    "DEFAULT_RENDERER_CLASSES": (
        [
            "rest_framework.renderers.JSONRenderer",
            "rest_framework.renderers.BrowsableAPIRenderer",
        ]
        if DEBUG
        else [
            "rest_framework.renderers.JSONRenderer",
        ]
    ),
}

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


os.environ["OPENBLAS_NUM_THREADS"] = "1"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-+xl&29!(=74y-3w%!x2&uxez6=v3_!12_hg!w87*5f6pszfhew"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "api",
    "rest_framework",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "temp_sense.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "temp_sense.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Bucharest"

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

APPEND_SLASH = False


CORS_ALLOWED_ORIGINS = [
    "https://temp-sense.cohe.ro",
]

CSRF_TRUSTED_ORIGINS = [
    "https://temp-sense.cohe.ro",
]

DAILY_EMAIL_SCHEDULED_HOUR = os.environ.get("DAILY_EMAIL_SCHEDULED_HOUR", 12)
OFFICE_EMAIL = os.environ.get("OFFICE_EMAIL", "office@cohe.ro")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp@cohe.ro")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_HOST_USERNAME = os.environ.get("EMAIL_HOST_USERNAME")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

CHIRPSTACK_URL = os.environ.get(
    "CHIRPSTACK_URL", "https://console.iot-wireless.com/api/devices"
)
CHIRPSTACK_API_TOKEN = os.environ.get("CHIRPSTACK_API_TOKEN")
CHIRPSTACK_APPLICATION_ID = os.environ.get("CHIRPSTACK_APPLICATION_ID")
CHIRPSTACK_DEVICE_PROFILE_ID = os.environ.get("CHIRPSTACK_DEVICE_PROFILE_ID")

DISCORD_SEND_MESSAGE_URL = os.environ.get("DISCORD_SEND_MESSAGE_URL")
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

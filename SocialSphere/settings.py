from datetime import timedelta
from pathlib import Path
import os
import dj_database_url
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-local-development-only-change-me")
DEBUG = os.environ.get("DEBUG", "False") == "True"
_hosts = os.environ.get("ALLOWED_HOSTS", "")
_allowed_hosts = [h.strip() for h in _hosts.split(",") if h.strip()]
_render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if _render_host: _allowed_hosts.append(_render_host)
ALLOWED_HOSTS = list(dict.fromkeys(_allowed_hosts + ["localhost", "127.0.0.1"]))
INSTALLED_APPS = ["django.contrib.admin","django.contrib.auth","django.contrib.contenttypes","django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles","rest_framework","corsheaders","TalkHub"]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware","django.middleware.security.SecurityMiddleware","django.contrib.sessions.middleware.SessionMiddleware","django.middleware.common.CommonMiddleware","django.middleware.csrf.CsrfViewMiddleware","django.contrib.auth.middleware.AuthenticationMiddleware","django.contrib.messages.middleware.MessageMiddleware","django.middleware.clickjacking.XFrameOptionsMiddleware"]
ROOT_URLCONF = "SocialSphere.urls"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "SocialSphere.wsgi.application"
DATABASES = {"default": dj_database_url.config(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}", conn_max_age=600, ssl_require=bool(os.environ.get("DATABASE_URL", "").startswith("postgres")))}
AUTH_PASSWORD_VALIDATORS = [{"NAME":"django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},{"NAME":"django.contrib.auth.password_validation.MinimumLengthValidator"},{"NAME":"django.contrib.auth.password_validation.CommonPasswordValidator"},{"NAME":"django.contrib.auth.password_validation.NumericPasswordValidator"}]
LANGUAGE_CODE="en-us"; TIME_ZONE="UTC"; USE_I18N=True; USE_TZ=True
STATIC_URL="static/"; MEDIA_URL="/media/"; MEDIA_ROOT=BASE_DIR / "media"; DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"
REST_FRAMEWORK={"DEFAULT_AUTHENTICATION_CLASSES":("rest_framework_simplejwt.authentication.JWTAuthentication",),"DEFAULT_PERMISSION_CLASSES":("rest_framework.permissions.IsAuthenticated",)}
SIMPLE_JWT={"AUTH_HEADER_TYPES":("Bearer",),"ACCESS_TOKEN_LIFETIME":timedelta(minutes=30),"REFRESH_TOKEN_LIFETIME":timedelta(days=1)}
_cors=os.environ.get("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS=[x.strip() for x in _cors.split(",") if x.strip()]
CORS_ALLOWED_ORIGINS=list(dict.fromkeys(CORS_ALLOWED_ORIGINS+["http://127.0.0.1:5500","http://localhost:5500","http://127.0.0.1:5501","http://localhost:5501","http://127.0.0.1:8000","http://localhost:8000"]))
CORS_ALLOW_ALL_ORIGINS=os.environ.get("CORS_ALLOW_ALL_ORIGINS","False")=="True"
if not DEBUG and _render_host: SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO","https"); SESSION_COOKIE_SECURE=True; CSRF_COOKIE_SECURE=True

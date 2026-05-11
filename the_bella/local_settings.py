
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = '2abbb66e6262d8a471b69c7jayedhossainjibona03a0c74bjibon69'

DEBUG = True

ALLOWED_HOSTS = ['*']
BASE_URL = "http://143.198.167.62"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Django Settings.py
# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': 'the_bela_db',
#        'USER': 'postgres',
#        'PASSWORD': 'bela355168AmDB',
#        'HOST': '127.0.0.1',
#        'PORT': '5432',
#    }
# }


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static"
]
STATIC_ROOT = BASE_DIR / "staticfiles"


# Media files (uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


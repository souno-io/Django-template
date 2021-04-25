# 此配置文件用于开发环境使用
from config.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'his': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'adg4',  # 这里写你上面配置tnsnames.ora中的名字
        'USER': '',
        'PASSWORD': '',
    },
}

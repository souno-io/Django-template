# 此配置文件用于开发环境使用
from config.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'No1_DataCenter',
        'USER': 'postgres',
        'PASSWORD': '1004426187',
        'HOST': '119.29.54.49',
        'PORT': '5432',
    },
    'his': {
        'ENGINE': 'django.db.backends.oracle',
        # 'HOST': '200.168.0.4',
        'NAME': 'adg4',  # 这里写你上面配置tnsnames.ora中的名字
        'USER': 'his',
        'PASSWORD': 'his',
    },
}

"""
Django settings for jwxzs_2 project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os,sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0,os.path.join(BASE_DIR,'extra apps'))
sys.path.insert(0,os.path.join(BASE_DIR,'apps'))

MEDIA_URL='/media/'
MEDIA_ROOT=os.path.join(BASE_DIR,'media/')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'cavul$s7vlryaiyi@$q0w+$wau$!%#^4ji5+=!(krn^ien0acr'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'django.forms',
    'users',
    'lessons',
    'scores',
    'xadmin',
    'crispy_forms',
    'corsheaders',
    'rest_framework',
    # 'rest_framework.authtoken',
    'message',
    'semesters',
    'ckeditor',
    'ckeditor_uploader',
    # 'rest_captcha',
]

AUTH_USER_MODEL='users.UserProfile'

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL=True

ROOT_URLCONF = 'jwxzs_2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'jwxzs_2.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jwxzs_2',
        'USER':'root',
        'PASSWORD':'1',
        'HOST':'127.0.0.1',
        'OPTIONS':{'init_command':'SET default_storage_engine=INNODB;'},
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


AUTHENTICATION_BACKENDS=(
    'users.views.CustomBackend',
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')


CKEDITOR_UPLOAD_PATH ='uploads/'

CKEDITOR_IMAGE_BACKEND = "pillow"

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        # 添加按钮在这里
        'toolbar_Custom': [
            ['Blockquote', 'CodeSnippet'],

        ],
    },
}

# CKEDITOR_CONFIGS = {
#     # 配置名是default时，django-ckeditor默认使用这个配置
#     'default': {
#         # 使用简体中文
#         'language':'zh-cn',
#         # 编辑器的宽高请根据你的页面自行设置
#         'width':'auto',
#         'height':'150px',
#         'image_previewText':' ',
#         'tabSpaces': 4,
#         'toolbar': 'Custom',
#         # 添加按钮在这里
#         'toolbar_Custom': [
#             ['Bold', 'Italic', 'Underline', 'Format', 'RemoveFormat'],
#             ['NumberedList', 'BulletedList'],
#             ['Blockquote', 'CodeSnippet'],
#             ['Image', 'Link', 'Unlink'],
#             ['Maximize']
#         ],
#         # 插件
#         'extraPlugins': ','.join(['codesnippet','uploadimage','widget','lineutils',]),
#     }
# }




REST_FRAMEWORK = {
    # 'DEFAULT_PAGINATION_CLASS':'rest_framework.pagination.PageNumberPagination',
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    # 'PAGE_SIZE':100,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.IsAuthenticated',
    # ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
    ),
    # 'DEFAULT_PAGINATION_CLASS':'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 10,
}




import datetime
JWT_AUTH={
    'JWT_EXPIRATION_DELTA':datetime.timedelta(days=7),
    'JWT_AUTH_HEADER_PREFIX':'JWT',
}


# VERIFICATIONCODE_SRC='/Users/vccccccc/PycharmProjects/jwxzs_2/spiders/VerificationCode/'
VERIFICATIONCODE_SRC='./VerificationCode/'


# SEMESTER_LIST=[
#     '2019/3/1 0:00:00',
#     '2018/9/1 0:00:00',
#     '2018/3/1 0:00:00',
# ]
#
# GRADE_LIST=[
#     '2015/9/1 0:00:00',
#     '2016/9/1 0:00:00',
#     '2017/9/1 0:00:00',
#     '2018/9/1 0:00:00',
# ]


from django.contrib.auth.hashers import make_password
PUBLIC_PASSWORD=make_password('jwxzspublicpassword')
#-*- coding:utf-8 -*-

# import os,django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
# django.setup()


from users.models import MyPassword
from utils.aes import return_my_words


MY_PASSWORD = MyPassword.objects.filter(user__is_active=True,user__is_student=True).first()
MY_WORD = return_my_words(MY_PASSWORD.password.encode())
MY_USERNAME=MY_PASSWORD.user.username

# print(MY_USERNAME)
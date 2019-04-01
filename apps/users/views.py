#-*- coding:utf-8 -*-
from django.shortcuts import render

# Create your views here.

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.contrib.auth.hashers import make_password

from spiders.student_dynamic import SpiderDynamicStudent

User=get_user_model()

class CustomBackend(ModelBackend):
    '''
    自定义用户认证
    '''
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user=User.objects.get(username=username)
            if user.check_password(password):
                return user
        except Exception as e:
            lenth=len(username)
            if lenth==10 or lenth==12:
                dynamic_student=SpiderDynamicStudent(str(username),str(password))
                # dynamic_student.test()
                sign_in=dynamic_student.sign_in()
                if sign_in:
                    pw=make_password(password=password)
                    studnet_user=User(username=username,password=pw,is_student=True)
                    studnet_user.save()
                    dynamic_student.get_all_data()
                    return studnet_user
                else:
                    return None
            elif lenth==5 or lenth==6:
                return None
            else:
                return None
            # return None





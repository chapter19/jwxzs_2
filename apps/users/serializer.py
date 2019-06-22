#-*- coding:utf-8 -*-
from .models import Major,Colloge,Class,Teacher,Student,StudentDetail,UserProfile,Department,MyPassword
from rest_framework import serializers
# from rest_captcha.serializers import RestCaptchaSerializer
from drf_haystack.serializers import HaystackSerializer
from .search_indexes import StudentIndex

from spiders.student_dynamic import SpiderDynamicStudent
from spiders.teacher_dynamic import SpiderDynamicTeacher
from utils.aes import make_my_password

from django.contrib.auth.hashers import make_password,check_password


class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Major
        fields='__all__'


class ClassMajorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Major
        fields=['name','subject','degree']


class CollogeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Colloge
        fields=['name','id']


class ClassSerializer(serializers.ModelSerializer):
    colloge=CollogeSerializer()
    major=ClassMajorSerializer()
    class Meta:
        model=Class
        fields=['name','colloge','major','grade']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Department
        fields=['id','name']



class TeacherSerializer(serializers.ModelSerializer):
    department=DepartmentSerializer()
    gender=serializers.SerializerMethodField()
    def get_gender(self, obj):
        return obj.get_gender_display()
    class Meta:
        model=Teacher
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    gender=serializers.SerializerMethodField()
    cla=ClassSerializer()
    def get_gender(self, obj):
        return obj.get_gender_display()
    class Meta:
        model=Student
        fields='__all__'


class StudentDetailSerializer(serializers.ModelSerializer):
    base_data=StudentSerializer()
    class Meta:
        model=StudentDetail
        fields='__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    gender=serializers.SerializerMethodField()
    def get_gender(self, obj):
        return obj.get_gender_display()
    class Meta:
        model=UserProfile
        fields=['username','name','gender','is_student','is_teacher','email','image']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    user_id=serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model=UserProfile
        fields=['image','email','user_id']
    def update(self, instance, validated_data):
        # user_id=validated_data.get('user_id')
        # if user_id!=instance.id:
        #     raise serializers.ValidationError({'detail':'你不能修改别人的信息！'})
        instance.email = validated_data.get('email', instance.email)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

#
# class CatptchaSerializer(RestCaptchaSerializer,serializers.Serializer):
#     pass

class StudentSearchSerializer(HaystackSerializer):
    class Meta:
        index_classes=[StudentIndex]
        fields=["name","id"]



class UserSerializer(serializers.ModelSerializer):
    student=StudentSerializer()
    teacher=TeacherSerializer()
    gender = serializers.SerializerMethodField()
    def get_gender(self, obj):
        return obj.get_gender_display()
    class Meta:
        model=UserProfile
        fields=['id','username','name','gender','is_student','is_teacher','image','student','teacher']


class UpdatePasswordSerializer(serializers.ModelSerializer):
    password=serializers.CharField(style={'input_type':'password'},required=True,write_only=True,min_length=5,max_length=20)
    # username=serializers.CharField(read_only=True)
    def update(self, instance, validated_data):
        word=validated_data.get('password')
        if instance.is_student:
            spd=SpiderDynamicStudent(instance.username,word)
            login=spd.sign_in()
            if login:
                instance.set_password(word)
                instance.save()
                try:
                    my_password=MyPassword.objects.get(user=instance)
                    my_password.password=make_my_password(word)
                    my_password.save()
                except:
                    print('my_password保存异常')
                return instance
            else:
                raise serializers.ValidationError({'detail':'密码和教务在线不一致，不允许设置！'})
        elif instance.is_teacher:
            spd=SpiderDynamicTeacher(instance.username,word)
            login=spd.sign_in()
            if login:
                instance.set_password(word)
                instance.save()
                try:
                    my_password = MyPassword.objects.get(user=instance)
                    my_password.password = make_my_password(word)
                    my_password.save()
                except:
                    print('my_password保存异常')
                return instance
            else:
                raise serializers.ValidationError({'detail':'密码和教务在线不一致，不允许设置！'})
        else:
            instance.set_password(word)
            instance.save()
            return instance
    class Meta:
        model=UserProfile
        fields=['password']


class ResetPasswordSerializer(serializers.ModelSerializer):
    username=serializers.CharField(required=True,max_length=12,min_length=5,label='学号/教号')
    password=serializers.CharField(required=True,style={'input_type':'password'},write_only=True,min_length=5,max_length=20)
    def create(self, validated_data):
        username=validated_data.get('username')
        password=validated_data.get('password')
        user=UserProfile.objects.filter(username=username)
        if user:
            user=user.first()
            if user.is_teacher:
                if not check_password(password,user.password):
                    spd=SpiderDynamicTeacher(username,password)
                    login=spd.sign_in()
                    if login:
                        user.set_password=password
                        user.save()
                        return user
                    else:
                        raise serializers.ValidationError({'detail':'账号或密码和教务在线不一致！'})
                else:
                    raise serializers.ValidationError({'detail':'输入密码就是当前账号密码，你可以直接登录，无需重置密码！'})
            elif user.is_student:
                if not check_password(password,user.password):
                    spd=SpiderDynamicStudent(username,password)
                    login=spd.sign_in()
                    if login:
                        user.set_password=password
                        user.save()
                        return user
                    else:
                        raise serializers.ValidationError({'detail':'账号或密码和教务在线不一致！'})
                else:
                    raise serializers.ValidationError({'detail':'输入密码就是当前账号密码，你可以直接登录，无需重置密码！'})
            else:
                raise serializers.ValidationError({'detail':'你当前的身份不是学生或教师，不能重置密码'})
        else:
            raise serializers.ValidationError({'detail':'学号或教号不存在，请检查是否填写正确'})
    class Meta:
        model=UserProfile
        fields=['username','password']

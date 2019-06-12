#-*- coding:utf-8 -*-
from rest_framework import serializers
from .models import Group,GroupAdministrator,DefGroup,DefGroupMember
from users.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    gender = serializers.SerializerMethodField()
    def get_gender(self, obj):
        return obj.get_gender_display()
    class Meta:
        model=UserProfile
        fields=['id','username','name','gender','is_student','is_teacher']

#初始化自定义组
class CreateDefGroupSerializer(serializers.Serializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    name=serializers.CharField(required=True,help_text='自定义群组名')
    id=serializers.IntegerField(read_only=True)
    def create(self, validated_data):
        creater_id=validated_data.get('user')
        name=validated_data.get('name')
        def_group=DefGroup.objects.filter(creater_id=creater_id,name=name)
        if not def_group:
            group = Group.objects.create(group_id=def_group.id, group_type=5, group_name=name)
            def_group=DefGroup.objects.create(creater_id=creater_id,name=name,group=group)
            GroupAdministrator.objects.create(group=group,admin_id=creater_id,if_super=True)
            DefGroupMember.objects.create(member_id=creater_id,def_group=def_group)
            return def_group
        else:
            raise serializers.ValidationError({'detail':'已存在同名小组，勿重复创建！'})
    class Meta:
        model=DefGroup
        fields=['user','name','id']


class DefGroupMemberListSerializer(serializers.ModelSerializer):
    member=UserProfileSerializer
    class Meta:
        model=DefGroupMember
        fields='__all__'


#自定义组详情
class RetrieveDefGroupSerializer(serializers.ModelSerializer):
    def_group_member=DefGroupMemberListSerializer()
    class Meta:
        model=DefGroup
        fields='__all__'


#更新自定义群组
class UpdateDefGroupSerializer(serializers.Serializer):
    # id = serializers.IntegerField(read_only=True)
    user_id=serializers.HiddenField(default=serializers.CurrentUserDefault())
    name=serializers.CharField(required=True,help_text='自定义群组名')
    def update(self, instance, validated_data):
        # id=validated_data.get('id')
        user_id=validated_data.get('user_id')
        admin=GroupAdministrator.objects.filter(admin_id=user_id,group=instance.group)
        if not admin:
            raise serializers.ValidationError({'detail':'你不是该组的管理员！不能更改'})
        instance.name = validated_data.get('name', instance.name)
        group=Group.objects.filter(group_type=5,group_id=instance.id)
        if group:
            group[0].group_name=instance.name
            group[0].save()
        else:
            print('未找到自定义群组')
        instance.save()
        return instance
        # user_id=validated_data.get('user')
    class Meta:
        model=DefGroup
        fields=['name',]

#添加组员
class CreateDefGroupMemberSerializer(serializers.Serializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # member=serializers.IntegerField(required=True,help_text='成员用户id')
    # def_group_id=serializers.IntegerField(required=True,help_text='自定义群组id')
    id=serializers.IntegerField(read_only=True)
    def create(self, validated_data):
        member=validated_data.get('member')
        def_group=validated_data.get('def_group')
        user_id=validated_data.get('user')
        if def_group[0].creater_id==user_id:
            # def_group_member=DefGroupMember.objects.filter(member_id=member_id,def)
            try:
                def_group_member=DefGroupMember.objects.create(member=member,def_group=def_group)
                return def_group_member
            except:
                raise serializers.ValidationError({'detail':'该组已存在该成员，勿重复添加！'})
        else:
            raise serializers.ValidationError({'detail':'你不是该组创建人，没有权限添加组员！'})
    class Meta:
        model=DefGroupMember
        fields=['member','def_group','id','user']



#group组列表
class ListGroupSerializer(serializers.ModelSerializer):
    group_type = serializers.SerializerMethodField()
    def get_group_type(self, obj):
        return obj.get_group_type_display()
    class Meta:
        model=Group
        fields=['group_name','group_id','group_type','id']


#退出该自定义组
# class LeaveDefGroupSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model=DefGroupMember
#         fields=[]





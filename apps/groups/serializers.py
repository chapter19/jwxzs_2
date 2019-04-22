#-*- coding:utf-8 -*-
from rest_framework import serializers
from .models import Group,GroupAdministrator,DefGroup,DefGroupMember


#初始化自定义组
class CreateDefGroupSerializer(serializers.Serializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    name=serializers.CharField(required=True,help_text='自定义群组名')
    def create(self, validated_data):
        creater_id=validated_data.get('user')
        name=validated_data.get('name')
        def_group=DefGroup.objects.filter(creater_id=creater_id,name=name)
        if not def_group:
            def_group=DefGroup.objects.create(creater_id=creater_id,name=name)
            group=Group.objects.create(group_id=def_group.id,group_type=5,group_name=name)
            GroupAdministrator.objects.create(group=group,admin_id=creater_id,if_super=True)
            DefGroupMember.objects.create(member_id=creater_id,def_group=def_group)
            return def_group
        else:
            raise serializers.ValidationError('已存在同名小组，勿重复创建！')
    class Meta:
        model=DefGroup
        fields=['user','name']


#自定义组详情
class RetrieveDefGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=DefGroup
        fields='__all__'


#更新自定义群组
class UpdateDefGroupSerializer(serializers.Serializer):
    # id = serializers.IntegerField(read_only=True)
    name=serializers.CharField(required=True,help_text='自定义群组名')
    def update(self, instance, validated_data):
        # id=validated_data.get('id')
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
    member_id=serializers.IntegerField(required=True,help_text='成员用户id')
    def_group_id=serializers.IntegerField(required=True,help_text='自定义群组id')
    def create(self, validated_data):
        member_id=validated_data.get('member_id')
        def_group_id=validated_data.get('def_group_id')
        def_group=DefGroup.objects.filter(id=def_group_id)
        if def_group:
            user_id=validated_data.get('user')
            if def_group[0].creater_id==user_id:
                # def_group_member=DefGroupMember.objects.filter(member_id=member_id,def)
                try:
                    def_group_member=DefGroupMember.objects.create(member_id=member_id,def_group_id=def_group_id)
                    return def_group_member
                except:
                    raise serializers.ValidationError('该组已存在该成员，勿重复添加！')
            else:
                raise serializers.ValidationError('你不是该组创建人，没有权限添加组员！')
        else:
            raise serializers.ValidationError('自定义组不存在！')

    class Meta:
        model=DefGroupMember
        fields=['member_id','def_group_id']


#group组列表
class ListGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=Group
        fields=['group_name','group_id','group_type']


#退出该自定义组
# class LeaveDefGroupSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model=DefGroupMember
#         fields=[]





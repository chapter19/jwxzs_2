#-*- coding:utf-8 -*-
from rest_framework import serializers

from message.models import Message,ReceiverMessage
from .models import CollectFriends,RecentContact
from users.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    gender = serializers.SerializerMethodField()
    def get_gender(self, obj):
        return obj.get_gender_display()
    class Meta:
        model=UserProfile
        fields=['id','username','name','gender','is_student','is_teacher','image']


class CollectFriendsSerializer(serializers.ModelSerializer):
    friend=UserProfileSerializer()
    user=UserProfileSerializer()
    # last_talk=serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    class Meta:
        model=CollectFriends
        fields=['friend','id','user']


class CreateCollectFriendsSerializer(serializers.Serializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    friend_id=serializers.IntegerField(required=True,help_text='好友用户id')
    id=serializers.IntegerField(read_only=True)
    def create(self, validated_data):
        user_id=validated_data.get('user_id')
        friend_id=validated_data.get('friend_id')
        if user_id!=friend_id:
            friend=CollectFriends.objects.filter(user_id=user_id,friend_id=friend_id)
            if not friend:
                user=UserProfile.objects.filter(id=user_id)
                if user:
                    user=user[0]
                    collect_friend=CollectFriends.objects.create(user=user,friend_id=friend_id)
                else:
                    raise serializers.ValidationError({'detail':'用户不存在！请检查并重新输入'})
                return collect_friend
            else:
                raise serializers.ValidationError({'detail':'你已关注了该好友，请不要重复关注'})
        else:
            raise serializers.ValidationError({'detail':'你不能关注你自己！'})
    class Meta:
        model=CollectFriends
        fields=['user_id','friend_id','id']


class RecentContactSerializer(serializers.Serializer):
    friend = UserProfileSerializer()
    class Meta:
        model=RecentContact
        dields=['friend','add_time','id']

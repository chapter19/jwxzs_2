#-*- coding:utf-8 -*-
from rest_framework import serializers

from message.models import Message,ReceiverMessage
from .models import CollectFriends,RecentContact
from users.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProfile
        fields=['id','username','name','gender','is_student']


class CollectFriendsSerializer(serializers.ModelSerializer):
    friend=UserProfileSerializer()
    # last_talk=serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    class Meta:
        model=CollectFriends
        fields=['friend',]


class CreateCollectFriendsSerializer(serializers.Serializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    friend_id=serializers.IntegerField(required=True,help_text='好友用户id')
    def create(self, validated_data):
        user_id=validated_data.get('user_id')
        friend_id=validated_data.get('friend_id')
        collect_friend=CollectFriends.objects.create(user_id=user_id,friend_id=friend_id)
        user=UserProfile.objects.get(id=user_id)
        title='关注了你'.format(user.name)
        body='我是{0}，我刚关注了你，为了方便联系快来关注我吧~'.format(user.name)
        message=Message.objects.create(title=title,body=body,sender=user,type=3)
        ReceiverMessage.objects.create(message=message,receiver_id=friend_id)
        return collect_friend
    class Meta:
        model=CollectFriends
        fields=['user_id','friend_id']


class RecentContactSerializer(serializers.Serializer):
    friend = UserProfileSerializer()
    class Meta:
        model=RecentContact
        dields=['friend','add_time']

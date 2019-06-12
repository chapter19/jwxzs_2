#-*- coding:utf-8 -*-
from rest_framework import serializers
from neo4j.create_graph import jwxzsgraph
import json
import requests
from neo4j.http_api import sess

class FindRelationViewSerializer(serializers.Serializer):
    userA_id=serializers.CharField(required=True,max_length=12,min_length=5,help_text='学生/教师A的id',write_only=True)
    userB_id=serializers.CharField(required=True,max_length=12,min_length=5,help_text='学生/教师B的id',write_only=True)
    # degree=serializers.IntegerField(required=False,max_value=5,min_value=2)
    def create(self, validated_data):
        userA_id=validated_data.get('userA_id')
        userB_id=validated_data.get('userB_id')
        a=sess.get_shortpath(userA_id=userA_id,userB_id=userB_id)
        return a


class FindUserChildNodeViewSerializer(serializers.Serializer):
    user_id=serializers.CharField(required=True,max_length=12,min_length=5,help_text='学生/教师的id',write_only=True)
    if_all=serializers.BooleanField(required=False,default=False,help_text='是否显示全部关系节点',write_only=True)
    page_num=serializers.IntegerField(required=False,default=1,help_text='页码，默认第一页',write_only=True)
    page_size=serializers.IntegerField(required=False,default=5,help_text='每页几条，默认5条',write_only=True)
    def create(self, validated_data):
        user_id=validated_data.get('user_id')
        if_all=validated_data.get('if_all')
        page_num=validated_data.get('page_num')
        page_size=validated_data.get('page_size')
        a=sess.get_user_page(userA_node_id=user_id,page_size=page_size,page_num=page_num,if_all=if_all)
        return a


class FindMyLessonNodeViewSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=True, max_length=12, min_length=5, help_text='学生/教师的id', write_only=True)
    if_all = serializers.BooleanField(required=False, default=False, help_text='是否显示全部关系节点', write_only=True)
    page_num = serializers.IntegerField(required=False, default=1, help_text='页码，默认第一页', write_only=True)
    page_size = serializers.IntegerField(required=False, default=5, help_text='每页几条，默认5条', write_only=True)
    def create(self, validated_data):
        user_id=validated_data.get('user_id')
        if_all=validated_data.get('if_all')
        page_num=validated_data.get('page_num')
        page_size=validated_data.get('page_size')
        a=sess.get_my_lesson(user_id=user_id,page_size=page_size,page_num=page_num,if_all=if_all)
        return a

class FindMyMajorNodeViewSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=True, max_length=12, min_length=10, help_text='学生的id', write_only=True)
    def create(self, validated_data):
        user_id=validated_data.get('user_id')
        a=sess.get_my_major(user_id=user_id)
        return a

class FindSimilarMajorNodeViewSerializer(serializers.Serializer):
    major_node_id=serializers.IntegerField(required=True,help_text='专业的节点的id',write_only=True)
    def create(self, validated_data):
        major_node_id=validated_data.get('major_node_id')
        a=sess.get_the_similar_major(major_node_id)
        return a


class FindMajorLessonNodeViewSerializer(serializers.Serializer):
    major_node_id=serializers.IntegerField(required=True,help_text='专业的节点的id',write_only=True)
    lesson_type=serializers.CharField(required=False,help_text='课程性质',write_only=True,default='专业限选')
    if_all_major_lesson=serializers.BooleanField(required=False,help_text='是否取全部专业课',write_only=True,default=False)
    def create(self, validated_data):
        major_node_id=validated_data.get('major_node_id')
        lesson_type=validated_data.get('lesson_type')
        if_all_major_lesson=validated_data.get('if_all_major_lesson')
        a=sess.get_major_lesson(major_node_id,lesson_type,if_all_major_lesson)
        return a



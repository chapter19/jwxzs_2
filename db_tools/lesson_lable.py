#-*- coding:utf-8 -*-


import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")  # project_name 项目名称
django.setup()


from lessons.models import Lesson

from subject.models import LessonLabels

from py2neo import Graph,NodeMatcher,Node

from jwxzs_2.settings import NEO4J_HOST,NEO4J_USERNAME,NEO4J_PASSWORD

graph = Graph(NEO4J_HOST,auth=(NEO4J_USERNAME,NEO4J_PASSWORD))

matcher=NodeMatcher(graph)
def get_lesson_node():
    lesson_nodes=matcher.match('Lesson')
    for le_no in lesson_nodes:
        labels=le_no.labels
        lesson_id=le_no['id']
        for lab in labels:
            if lab!='Lesson':
                try:
                    print(LessonLabels.objects.create(lesson_id=lesson_id,label=lab))
                except:
                    print('label已存在')


if __name__ == '__main__':
    get_lesson_node()





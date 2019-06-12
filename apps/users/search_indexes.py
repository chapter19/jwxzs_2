#-*- coding:utf-8 -*-

from haystack import indexes
from .models import Student

class StudentIndex(indexes.SearchIndex,indexes.Indexable):
    text=indexes.CharField(document=True,use_template=True)
    name=indexes.CharField(model_attr='name')
    id=indexes.CharField(model_attr='id')

    # @staticmethod
    # def prepare_autocomplete(obj):
    #     return " ".join((obj.name,obj.id))

    def get_model(self):
        return Student
    def index_queryset(self,using=None):
        return self.get_model().objects.all()













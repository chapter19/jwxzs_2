#-*- coding:utf-8 -*-

from django import forms

class GradeForm(forms.Form):
    grade=forms.IntegerField(min_value=15,max_value=99,required=True)
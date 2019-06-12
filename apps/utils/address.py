#-*- coding:utf-8 -*-

import requests
import json

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
django.setup()

from jwxzs_2.settings import AMAP_KEY
from logs.models import Ip

def get_address(ip):
    ips=Ip.objects.filter(ip=ip)
    if not ips:
        url='https://restapi.amap.com/v3/ip'
        data={
            'ip':ip,
            'output':'json',
            'key':AMAP_KEY
        }
        data=requests.get(url,data)
        print(data.text)
        dic=json.loads(data.text)
        address=dic['province']+dic['city']
        print(address)
        try:
            Ip.objects.create(ip=ip,address=address,adcode=dic['adcode'],rectangle=dic['rectangle'])
        except:
            print('ip添加失败')
        return address
    else:
        return ips[0].address

if __name__ == '__main__':
    get_address('39.176.195.59')

#-*- coding:utf-8 -*-

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
django.setup()

from jwxzs_2.settings import VERIFICATIONCODE_SRC,GRADE_LIST

import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import uuid,os,time
from users.models import Colloge,Class,Student,Major
from lessons.models import MajorLesson,Lesson

class SpiderStaticStudent:
    def __init__(self,id,password):
        self.id=id
        self.password=password
        self.__s=requests.Session()

    # get方法请求，获得隐藏参数 viewstate、eventvalidation
    def __get_hid_data(self, url, error_time_limit=7,timeout=4):
        try:
            b = self.__s.get(url, timeout=timeout)
            soup = BeautifulSoup(b.text, 'html5lib')
            __VIEWSTATE = soup.select('input[id="__VIEWSTATE"]')
            __EVENTVALIDATION = soup.select('input[id="__EVENTVALIDATION"]')
            return __VIEWSTATE[0].get('value'), __EVENTVALIDATION[0].get('value')
        except:
            error_time_limit -= 1
            if error_time_limit > 0:
                print('__get_hid_data timeout, retrying。。')
                return self.__get_hid_data(url=url, error_time_limit=error_time_limit)
            else:
                return 0

    #获取隐藏值和验证码
    def __get_hid_data_and_vecode(self,url,error_time_limit=7,timeout=2):
        try:
            b=self.__s.get(url,timeout=timeout)
            soup=BeautifulSoup(b.text,'html5lib')
            # print(soup)
            __VIEWSTATE = soup.select('input[id="__VIEWSTATE"]')
            __EVENTVALIDATION = soup.select('input[id="__EVENTVALIDATION"]')
            photo_url='http://jwc.jxnu.edu.cn/Portal/'+soup.select('#_ctl0_cphContent_imgPasscode')[0].get('src')
            # print(photo_url)
            d=self.__s.get(photo_url)
            vecode_name=str(uuid.uuid1())+'.png'
            src=VERIFICATIONCODE_SRC+vecode_name
            # print(__VIEWSTATE[0].get('value'),__EVENTVALIDATION[0].get('value'),vecode_name)
            with open(src,'wb') as vecode:
                vecode.write(d.content)
                vecode.close()
            return __VIEWSTATE[0].get('value'),__EVENTVALIDATION[0].get('value'),vecode_name
        except:
            error_time_limit-=1
            if error_time_limit>0:
                print('__get_hid_data_and_vecode timeout, retrying。。')
                return self.__get_hid_data_and_vecode(url=url,error_time_limit=error_time_limit,timeout=timeout)
            else:
                return 0

    #验证码识别
    def verification_code(self):
        try:
            print('verification_code is working。。')
            url1 = 'http://jwc.jxnu.edu.cn/Portal/LoginAccount.aspx?t=account'
            hid=self.__get_hid_data_and_vecode(url=url1)
            src=VERIFICATIONCODE_SRC+hid[2]
            # v=get_vectorCompare(src)
            # new_src='./VerificationCode/'+v+'.png'
            # os.rename(src,new_src)
            # print(v)
            # print(src)
            image=Image.open(src)
            x, y = image.size
            p = Image.new('RGBA', image.size, (255, 255, 255))
            p.paste(image, (0, 0, x, y), image)
            # p.save('src')
            # p.show()
            # 转化为灰度图像
            image=p.convert('L')
            threshold=80
            table=[]
            for i in range(256):
                if i < threshold:
                    table.append(0)
                else:
                    table.append(1)
            image=image.point(table,'1')
            # image.show()
            w,h=image.size
            # print(w,h)
            ppp = Image.new('RGBA', image.size, (255, 255, 255))
            ppp.paste(image, (0, 0, w, h))
            iii=ppp.resize((w,h))
            # iii.show()
            os.remove(src)
            iii.save(src)
            pppp=Image.open(src)
            # iii=image.resize((w*2,h*2))
            # iii.show()
            result=str(pytesseract.image_to_string(pppp,lang='eng')).replace('.','').replace(',','').replace('(','').replace(')','').replace(':','').replace('/','').replace('[','').replace(']','').strip()
            os.remove(src)
            print(result)
            # new_src='./VerificationCode/'+result+'.png'
            # os.rename(src,new_src)
            # print(result)
            return hid[0],hid[1],result
        except:
            print('verification_code failed.')
            return None

    # 登录
    def sign_in(self,limit_time=10,timeout=5):
        try:
            url1 = 'http://jwc.jxnu.edu.cn/Portal/LoginAccount.aspx?t=account'
            hid= self.verification_code()
            #登录表单
            data1={
                '__VIEWSTATE':hid[0],
                '__EVENTVALIDATION':hid[1],
                '_ctl0:cphContent:ddlUserType':'Student',
                '_ctl0:cphContent:txtUserNum':self.id,
                '_ctl0:cphContent:txtPassword':self.password,
                '_ctl0:cphContent:btnLogin':'登录',
                '_ctl0:cphContent:txtCheckCode':hid[2],
            }
            b=self.__s.post(url1,data=data1,timeout=timeout)
            soup=BeautifulSoup(b.text,'html5lib')
            # print(soup)
            jwtz=soup.select('#jwtz')
            # print(jwtz)
            if jwtz!=[]:
                print('sign in successfluly!')
                return 1
            else:
                limit_t=limit_time-1
                print('sign in fail')
                if limit_t>0:
                    time.sleep(1)
                    print('sign_in failed, retrying。。')
                    return self.sign_in(limit_time=limit_t,timeout=timeout)
                else:
                    return None
                # print(b.text)
        except:
            limit_ti=limit_time-1
            if limit_ti > 0:
                print('sign_in timeout, retrying。。')
                return self.sign_in(limit_time=limit_ti,timeout=timeout)
            else:
                return None


    #插入学院
    def __CollogeToObject(self,data):
        colloge=Colloge()
        colloge.id=data['id']
        colloge.name=data['name']
        colloge.post_code=data['post_code']
        try:
            colloge.save()
        except:
            print('colloge exsit')


    def get_colloges(self,limit_time=7,timeout=5):
        try:
            url=r'http://jwc.jxnu.edu.cn/User/default.aspx?&&code=119&uctl=MyControl%5call_searchstudent.ascx'
            hid_data=self.__get_hid_data(url)
            data={
                '__EVENTTARGET':'_ctl1$rbtType$1',
                '__EVENTARGUMENT':'',
                '__LASTFOCUS':'',
                '__VIEWSTATE':hid_data[0],
                '__EVENTVALIDATION':hid_data[1],
                '_ctl1:rbtType':'College',
                '_ctl1:txtKeyWord':'请输入关键字!',
                '_ctl1:ddlType':'姓名',
                '_ctl1:ddlSQLType':'精确'
            }
            wb_data=self.__s.post(url=url,data=data,timeout=timeout)
            soup=BeautifulSoup(wb_data.text,'lxml')

            options=soup.select('#_ctl1_ddlCollege > option')
            for op in options:
                post_code=op.get('value')
                data={
                    'id':post_code.strip(),
                    'post_code':post_code,
                    'name':op.get_text().strip()
                }
                try:
                    self.__CollogeToObject(data)
                    print(data)
                except:
                    print('insert colloge already')
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_colloges timeout, retrying。。')
                return self.get_colloges(limit_time=limit_ti,timeout=timeout)
            else:
                return None


    def __get_start_class_hid(self,limit_time=7,timeout=4):
        try:
            url = r'http://jwc.jxnu.edu.cn/User/default.aspx?&&code=119&uctl=MyControl%5call_searchstudent.ascx'
            hid_data = self.__get_hid_data(url)
            data = {
                '__EVENTTARGET': '_ctl1$rbtType$1',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': hid_data[0],
                '__EVENTVALIDATION': hid_data[1],
                '_ctl1:rbtType': 'College',
                '_ctl1:txtKeyWord': '请输入关键字!',
                '_ctl1:ddlType': '姓名',
                '_ctl1:ddlSQLType': '精确'
            }
            wb_data = self.__s.post(url=url, data=data)
            soup=BeautifulSoup(wb_data.text,'html5lib')
            __VIEWSTATE = soup.select('input[id="__VIEWSTATE"]')
            __EVENTVALIDATION = soup.select('input[id="__EVENTVALIDATION"]')
            return __VIEWSTATE[0].get('value'), __EVENTVALIDATION[0].get('value')
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('__get_start_class_hid timeout, retrying。。')
                return self.__get_start_class_hid(limit_time=limit_ti, timeout=timeout)
            else:
                return None

    def __ClassToObject(self,data):
        cla=Class()
        cla.id=data['id']
        cla.name=data['name']
        cla.post_code=data['post_code']
        cla.colloge=data['colloge']
        cla.grade=data['grade']
        try:
            cla.save()
        except:
            print('class exsit')

    def __clena_grade(self,str):
        try:
            grade=int(str.split('级')[0].strip())
            return grade
        except:
            return None


    def get_one_colloge_classes(self,colloge_code='46000   ',limit_time=5,timeout=4):
        try:
            url = r'http://jwc.jxnu.edu.cn/User/default.aspx?&&code=119&uctl=MyControl%5call_searchstudent.ascx'
            # hid_data = self.__get_hid_data(url)
            hid_data = self.__get_start_class_hid()
            '''
    
            __EVENTTARGET: 
            __EVENTARGUMENT: 
            __LASTFOCUS: 
            __VIEWSTATE: /wEPDwUJNzIzMTk0NzYzD2QWAgIBD2QWCgIBDw8WAh4EVGV4dAUpMjAxOeW5tDPmnIgxMuaXpSDmmJ/mnJ/kuowmbmJzcDvmpI3moJHoioJkZAIFDw8WAh8ABRvlvZPliY3kvY3nva7vvJrlrabnlJ/kv6Hmga9kZAIHDw8WAh8ABS8gICDmrKLov47mgqjvvIwoMjAxNjI2NzAzMDc5LFN0dWRlbnQpIOW8oOacrOiJr2RkAgoPZBYEAgEPDxYCHghJbWFnZVVybAVFLi4vTXlDb250cm9sL0FsbF9QaG90b1Nob3cuYXNweD9Vc2VyTnVtPTIwMTYyNjcwMzA3OSZVc2VyVHlwZT1TdHVkZW50ZGQCAw8WAh8ABbklPGRpdiBpZD0nbWVudVBhcmVudF8wJyBjbGFzcz0nbWVudVBhcmVudCcgb25jbGljaz0nbWVudUdyb3VwU3dpdGNoKDApOyc+5oiR55qE5L+h5oGvPC9kaXY+PGRpdiBpZD0nbWVudUdyb3VwMCcgY2xhc3M9J21lbnVHcm91cCc+PERpdiBjbGFzcz0nbWVudUl0ZW0nIHRpdGxlPSfor77nqIvooagnPjxhIGhyZWY9ImRlZmF1bHQuYXNweD8mY29kZT0xMTEmJnVjdGw9TXlDb250cm9sXHhmel9rY2IuYXNjeCZNeUFjdGlvbj1QZXJzb25hbCIgdGFyZ2V0PSdwYXJlbnQnPuivvueoi+ihqDwvYT48L2Rpdj48RGl2IGNsYXNzPSdtZW51SXRlbScgdGl0bGU9J+WfuuacrOS/oeaBryc+PGEgaHJlZj0iLi5cTXlDb250cm9sXFN0dWRlbnRfSW5mb3JDaGVjay5hc3B4IiB0YXJnZXQ9J19ibGFuayc+5Z+65pys5L+h5oGvPC9hPjwvZGl2PjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0n5L+u5pS55a+G56CBJz48YSBocmVmPSJkZWZhdWx0LmFzcHg/JmNvZGU9MTEwJiZ1Y3RsPU15Q29udHJvbFxwZXJzb25hbF9jaGFuZ2Vwd2QuYXNjeCIgdGFyZ2V0PSdwYXJlbnQnPuS/ruaUueWvhueggTwvYT48L2Rpdj48RGl2IGNsYXNzPSdtZW51SXRlbScgdGl0bGU9J+WtpuexjemihOitpic+PGEgaHJlZj0iamF2YXNjcmlwdDpPcGVuV2luZG93KCd4ZnpfYnlzaC5hc2N4JkFjdGlvbj1QZXJzb25hbCcpOyIgdGFyZ2V0PScnPuWtpuexjemihOitpjwvYT48L2Rpdj48RGl2IGNsYXNzPSdtZW51SXRlbScgdGl0bGU9J+aWsOeUn+WvvOW4iCc+PGEgaHJlZj0iZGVmYXVsdC5hc3B4PyZjb2RlPTIxNCYmdWN0bD1NeUNvbnRyb2xcc3R1ZGVudF9teXRlYWNoZXIuYXNjeCIgdGFyZ2V0PSdwYXJlbnQnPuaWsOeUn+WvvOW4iDwvYT48L2Rpdj48RGl2IGNsYXNzPSdtZW51SXRlbScgdGl0bGU9J+ivvueoi+aIkOe7qSc+PGEgaHJlZj0iamF2YXNjcmlwdDpPcGVuV2luZG93KCd4ZnpfY2ouYXNjeCZBY3Rpb249UGVyc29uYWwnKTsiIHRhcmdldD0nJz7or77nqIvmiJDnu6k8L2E+PC9kaXY+PERpdiBjbGFzcz0nbWVudUl0ZW0nIHRpdGxlPSfmiYvmnLrlj7fnoIEnPjxhIGhyZWY9Ii4uXE15Q29udHJvbFxQaG9uZS5hc3B4IiB0YXJnZXQ9J19ibGFuayc+5omL5py65Y+356CBPC9hPjwvZGl2PjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0n5a626ZW/55m75b2VJz48YSBocmVmPSJkZWZhdWx0LmFzcHg/JmNvZGU9MjAzJiZ1Y3RsPU15Q29udHJvbFxKel9zdHVkZW50c2V0dGluZy5hc2N4IiB0YXJnZXQ9J3BhcmVudCc+5a626ZW/55m75b2VPC9hPjwvZGl2PjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0n5Y+M5LiT5Lia5Y+M5a2m5L2N6K++56iL5a6J5o6S6KGoJz48YSBocmVmPSIuLlxNeUNvbnRyb2xcRGV6eV9rYi5hc3B4IiB0YXJnZXQ9J19ibGFuayc+5Y+M5LiT5Lia5Y+M5a2m5L2N6K++56iL5a6J5o6S6KGoPC9hPjwvZGl2PjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0n55u454mH5pu05o2i55Sz6K+3Jz48YSBocmVmPSIuLlxNeUNvbnRyb2xccGhvdG9fcmVwbGFjZS5hc3B4IiB0YXJnZXQ9J19ibGFuayc+55u454mH5pu05o2i55Sz6K+3PC9hPjwvZGl2PjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0n5a2m5Lmg5L2T6aqMJz48YSBocmVmPSIuLlxNeUNvbnRyb2xcU3R1ZGVudF9NeVJlcG9ydC5hc3B4IiB0YXJnZXQ9J19ibGFuayc+5a2m5Lmg5L2T6aqMPC9hPjwvZGl2PjwvZGl2PjxkaXYgaWQ9J21lbnVQYXJlbnRfMScgY2xhc3M9J21lbnVQYXJlbnQnIG9uY2xpY2s9J21lbnVHcm91cFN3aXRjaCgxKTsnPuWFrOWFseacjeWKoTwvZGl2PjxkaXYgaWQ9J21lbnVHcm91cDEnIGNsYXNzPSdtZW51R3JvdXAnPjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0n5Z+55YW75pa55qGIJz48YSBocmVmPSJkZWZhdWx0LmFzcHg/JmNvZGU9MTA0JiZ1Y3RsPU15Q29udHJvbFxhbGxfanhqaC5hc2N4IiB0YXJnZXQ9J3BhcmVudCc+5Z+55YW75pa55qGIPC9hPjwvZGl2PjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0n6K++56iL5L+h5oGvJz48YSBocmVmPSJkZWZhdWx0LmFzcHg/JmNvZGU9MTE2JiZ1Y3RsPU15Q29udHJvbFxhbGxfY291cnNlc2VhcmNoLmFzY3giIHRhcmdldD0ncGFyZW50Jz7or77nqIvkv6Hmga88L2E+PC9kaXY+PERpdiBjbGFzcz0nbWVudUl0ZW0nIHRpdGxlPSflvIDor77lronmjpInPjxhIGhyZWY9Ii4uXE15Q29udHJvbFxQdWJsaWNfS2thcC5hc3B4IiB0YXJnZXQ9J19ibGFuayc+5byA6K++5a6J5o6SPC9hPjwvZGl2PjxEaXYgY2xhc3M9J21lbnVJdGVtT24nIHRpdGxlPSflrabnlJ/kv6Hmga8nPjxhIGhyZWY9ImRlZmF1bHQuYXNweD8mY29kZT0xMTkmJnVjdGw9TXlDb250cm9sXGFsbF9zZWFyY2hzdHVkZW50LmFzY3giIHRhcmdldD0ncGFyZW50Jz7lrabnlJ/kv6Hmga88L2E+PC9kaXY+PERpdiBjbGFzcz0nbWVudUl0ZW0nIHRpdGxlPSfmlZnlt6Xkv6Hmga8nPjxhIGhyZWY9ImRlZmF1bHQuYXNweD8mY29kZT0xMjAmJnVjdGw9TXlDb250cm9sXGFsbF90ZWFjaGVyLmFzY3giIHRhcmdldD0ncGFyZW50Jz7mlZnlt6Xkv6Hmga88L2E+PC9kaXY+PERpdiBjbGFzcz0nbWVudUl0ZW0nIHRpdGxlPSfnn63kv6HlubPlj7AnPjxhIGhyZWY9ImRlZmF1bHQuYXNweD8mY29kZT0xMjImJnVjdGw9TXlDb250cm9sXG1haWxfbGlzdC5hc2N4IiB0YXJnZXQ9J3BhcmVudCc+55+t5L+h5bmz5Y+wPC9hPjwvZGl2PjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0n5pWZ5a6k5pWZ5a2m5a6J5o6SJz48YSBocmVmPSIuLlxNeUNvbnRyb2xccHVibGljX2NsYXNzcm9vbS5hc3B4IiB0YXJnZXQ9J19ibGFuayc+5pWZ5a6k5pWZ5a2m5a6J5o6SPC9hPjwvZGl2PjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0n5Y+M5a2m5L2N6K++56iL5oiQ57upJz48YSBocmVmPSJqYXZhc2NyaXB0Ok9wZW5XaW5kb3coJ2RlenlfY2ouYXNjeCZBY3Rpb249UGVyc29uYWwnKTsiIHRhcmdldD0nJz7lj4zlrabkvY3or77nqIvmiJDnu6k8L2E+PC9kaXY+PERpdiBjbGFzcz0nbWVudUl0ZW0nIHRpdGxlPSfmr5XkuJrnlJ/lm77lg4/ph4fpm4bkv6Hmga/moKHlr7knPjxhIGhyZWY9Ii4uXE15Q29udHJvbFxUWENKX0luZm9yQ2hlY2suYXNweCIgdGFyZ2V0PSdfYmxhbmsnPuavleS4mueUn+WbvuWDj+mHh+mbhuS/oeaBr+agoeWvuTwvYT48L2Rpdj48RGl2IGNsYXNzPSdtZW51SXRlbScgdGl0bGU9J+acn+acq+aIkOe7qeafpeivoic+PGEgaHJlZj0iamF2YXNjcmlwdDpPcGVuV2luZG93KCd4ZnpfVGVzdF9jai5hc2N4Jyk7IiB0YXJnZXQ9Jyc+5pyf5pyr5oiQ57up5p+l6K+iPC9hPjwvZGl2PjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0n5pyf5pyr5oiQ57up5p+l5YiG55Sz6K+3Jz48YSBocmVmPSJqYXZhc2NyaXB0Ok9wZW5XaW5kb3coJ0Nmc3FfU3R1ZGVudC5hc2N4Jyk7IiB0YXJnZXQ9Jyc+5pyf5pyr5oiQ57up5p+l5YiG55Sz6K+3PC9hPjwvZGl2PjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0n6KGl57yT6ICD6ICD6K+V5a6J5o6SJz48YSBocmVmPSJqYXZhc2NyaXB0Ok9wZW5XaW5kb3coJ3hmel9UZXN0X0JISy5hc2N4Jyk7IiB0YXJnZXQ9Jyc+6KGl57yT6ICD6ICD6K+V5a6J5o6SPC9hPjwvZGl2PjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0n5a2m5Lmg6Zeu562UJz48YSBocmVmPSJkZWZhdWx0LmFzcHg/JmNvZGU9MTU5JiZ1Y3RsPU15Q29udHJvbFxBbGxfU3R1ZHlfTGlzdC5hc2N4IiB0YXJnZXQ9J3BhcmVudCc+5a2m5Lmg6Zeu562UPC9hPjwvZGl2PjwvZGl2PjxkaXYgaWQ9J21lbnVQYXJlbnRfMicgY2xhc3M9J21lbnVQYXJlbnQnIG9uY2xpY2s9J21lbnVHcm91cFN3aXRjaCgyKTsnPuaVmeWtpuS/oeaBrzwvZGl2PjxkaXYgaWQ9J21lbnVHcm91cDInIGNsYXNzPSdtZW51R3JvdXAnPjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0n572R5LiK6K+E5pWZJz48YSBocmVmPSJqYXZhc2NyaXB0Ok9wZW5XaW5kb3coJ3BqX3N0dWRlbnRfaW5kZXguYXNjeCcpOyIgdGFyZ2V0PScnPue9keS4iuivhOaVmTwvYT48L2Rpdj48RGl2IGNsYXNzPSdtZW51SXRlbScgdGl0bGU9J+aVmeWKoeaEj+ingeeusSc+PGEgaHJlZj0iLi4vRGVmYXVsdC5hc3B4P0FjdGlvbj1BZHZpc2UiIHRhcmdldD0nX2JsYW5rJz7mlZnliqHmhI/op4HnrrE8L2E+PC9kaXY+PERpdiBjbGFzcz0nbWVudUl0ZW0nIHRpdGxlPSfmnJ/mnKvogIPor5XlronmjpInPjxhIGhyZWY9ImRlZmF1bHQuYXNweD8mY29kZT0xMjkmJnVjdGw9TXlDb250cm9sXHhmel90ZXN0X3NjaGVkdWxlLmFzY3giIHRhcmdldD0ncGFyZW50Jz7mnJ/mnKvogIPor5XlronmjpI8L2E+PC9kaXY+PERpdiBjbGFzcz0nbWVudUl0ZW0nIHRpdGxlPSfovoXkv67lj4zkuJPkuJrlj4zlrabkvY3miqXlkI0nPjxhIGhyZWY9ImphdmFzY3JpcHQ6T3BlbldpbmRvdygnRGV6eV9ibS5hc2N4Jyk7IiB0YXJnZXQ9Jyc+6L6F5L+u5Y+M5LiT5Lia5Y+M5a2m5L2N5oql5ZCNPC9hPjwvZGl2PjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0nMjAxOOe6p+acrOenkeWtpueUn+i9rOS4k+S4muaKpeWQjSc+PGEgaHJlZj0iLi5cTXlDb250cm9sXHp6eV9zdHVkZW50X3NxLmFzcHgiIHRhcmdldD0nX2JsYW5rJz4yMDE457qn5pys56eR5a2m55Sf6L2s5LiT5Lia5oql5ZCNPC9hPjwvZGl2PjxEaXYgY2xhc3M9J21lbnVJdGVtJyB0aXRsZT0n5q+V5Lia55Sf5q+V5Lia44CB5a2m5L2N55Sz6K+3Jz48YSBocmVmPSIuLlxNeUNvbnRyb2xcQnl4d1NxX3N0dWRlbnQuYXNweCIgdGFyZ2V0PSdfYmxhbmsnPuavleS4mueUn+avleS4muOAgeWtpuS9jeeUs+ivtzwvYT48L2Rpdj48L2Rpdj5kAgwPZBYCZg9kFhACAQ8QZGQWAQIBZAIDDw8WAh4HVmlzaWJsZWhkZAIFDxAPFgIfAmhkZBYBZmQCBw8QDxYCHwJoZGQWAWZkAgkPEA8WCB4NRGF0YVRleHRGaWVsZAUM5Y2V5L2N5ZCN56ewHg5EYXRhVmFsdWVGaWVsZAUJ5Y2V5L2N5Y+3HgtfIURhdGFCb3VuZGcfAmdkEBUbEui0ouaUv+mHkeiejeWtpumZohLln47luILlu7rorr7lrabpmaIS5Yid562J5pWZ6IKy5a2m6ZmiFeWcsOeQhuS4jueOr+Wig+WtpumZohLlhazotLnluIjojIPnlJ/pmaIS5Zu96ZmF5pWZ6IKy5a2m6ZmiEuWMluWtpuWMluW3peWtpumZohvorqHnrpfmnLrkv6Hmga/lt6XnqIvlrabpmaIS57un57ut5pWZ6IKy5a2m6ZmiDOaVmeiCsuWtpumZoh7lhpvkuovmlZnnoJTpg6jvvIjmraboo4Xpg6jvvIkS56eR5a2m5oqA5pyv5a2m6ZmiG+WOhuWPsuaWh+WMluS4juaXhea4uOWtpumZohXpqazlhYvmgJ3kuLvkuYnlrabpmaIM576O5pyv5a2m6ZmiDOi9r+S7tuWtpumZognllYblrabpmaIS55Sf5ZG956eR5a2m5a2m6ZmiG+aVsOWtpuS4juS/oeaBr+enkeWtpuWtpumZogzkvZPogrLlrabpmaIP5aSW5Zu96K+t5a2m6ZmiCeaWh+WtpumZohvniannkIbkuI7pgJrkv6HnlLXlrZDlrabpmaIM5b+D55CG5a2m6ZmiFeaWsOmXu+S4juS8oOaSreWtpumZogzpn7PkuZDlrabpmaIM5pS/5rOV5a2m6ZmiFRsINjgwMDAgICAINjMwMDAgICAIODIwMDAgICAINDgwMDAgICAINTcwMDAgICAINjkwMDAgICAINjEwMDAgICAINjIwMDAgICAINDUwICAgICAINTAwMDAgICAIMzcwMDAgICAIODEwMDAgICAINTgwMDAgICAINDYwMDAgICAINjUwMDAgICAINjcwMDAgICAINTQwMDAgICAINjYwMDAgICAINTUwMDAgICAINTYwMDAgICAINTIwMDAgICAINTEwMDAgICAINjAwMDAgICAINDkwMDAgICAINjQwMDAgICAINTMwMDAgICAINTkwMDAgICAUKwMbZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnFgFmZAILDxAPFggfAwUM54+t57qn5ZCN56ewHwQFCeePree6p+WPtx8FZx8CZ2QQFSQtMTjnuqfkvJrorqHlraYx54+tICAgICAgICAgICAgICAgICAgICAgICAgICAgLTE457qn5Lya6K6h5a2mMuePrSAgICAgICAgICAgICAgICAgICAgICAgICAgIC0xOOe6p+S8muiuoeWtpjPnj60gICAgICAgICAgICAgICAgICAgICAgICAgICAtMTjnuqfph5Hono3lraYx54+tICAgICAgICAgICAgICAgICAgICAgICAgICAgLTE457qn6YeR6J6N5a2mMuePrSAgICAgICAgICAgICAgICAgICAgICAgICAgIC0xOOe6p+e7j+a1juWtpjHnj60gICAgICAgICAgICAgICAgICAgICAgICAgICAtMTjnuqfnu4/mtY7lraYy54+tICAgICAgICAgICAgICAgICAgICAgICAgICAgLTE457qn57uP5rWO5a2mM+ePrSAgICAgICAgICAgICAgICAgICAgICAgICAgIC0xN+e6p+S8muiuoeWtpjHnj60gICAgICAgICAgICAgICAgICAgICAgICAgICAtMTfnuqfkvJrorqHlraYy54+tICAgICAgICAgICAgICAgICAgICAgICAgICAgLTE357qn6YeR6J6N5a2mMeePrSAgICAgICAgICAgICAgICAgICAgICAgICAgIC0xN+e6p+mHkeiejeWtpjLnj60gICAgICAgICAgICAgICAgICAgICAgICAgICAtMTfnuqfnu4/mtY7lrabnj60gICAgICAgICAgICAgICAgICAgICAgICAgICAgLTE357qn5Lya6K6h5a2mM+ePrSAgICAgICAgICAgICAgICAgICAgICAgICAgIC0xN+e6p+S8muiuoeWtpjTnj60gICAgICAgICAgICAgICAgICAgICAgICAgICAtMTfnuqfkvJrorqHlraY154+tICAgICAgICAgICAgICAgICAgICAgICAgICAgLTE357qn6YeR6J6N5a2mM+ePrSAgICAgICAgICAgICAgICAgICAgICAgICAgIC0xN+e6p+mHkeiejeWtpjTnj60gICAgICAgICAgICAgICAgICAgICAgICAgICAtMTbnuqfkvJrorqHlraYx54+tICAgICAgICAgICAgICAgICAgICAgICAgICAgLTE257qn5Lya6K6h5a2mMuePrSAgICAgICAgICAgICAgICAgICAgICAgICAgIC0xNue6p+S8muiuoeWtpjPnj60gICAgICAgICAgICAgICAgICAgICAgICAgICAtMTbnuqfph5Hono3lraYx54+tICAgICAgICAgICAgICAgICAgICAgICAgICAgLTE257qn6YeR6J6N5a2mMuePrSAgICAgICAgICAgICAgICAgICAgICAgICAgIC0xNue6p+e7j+a1juWtpuePrSAgICAgICAgICAgICAgICAgICAgICAgICAgICAtMTbnuqfkvJrorqHlraY054+tICAgICAgICAgICAgICAgICAgICAgICAgICAgLTE257qn5Lya6K6h5a2mNeePrSAgICAgICAgICAgICAgICAgICAgICAgICAgIC0xNue6p+mHkeiejeWtpjPnj60gICAgICAgICAgICAgICAgICAgICAgICAgICAtMTbnuqfph5Hono3lraY054+tICAgICAgICAgICAgICAgICAgICAgICAgICAgLjE157qn6LSi5Yqh566h55CG54+tICAgICAgICAgICAgICAgICAgICAgICAgICAtMTXnuqfkvJrorqHlraYx54+tICAgICAgICAgICAgICAgICAgICAgICAgICAgLTE157qn5Lya6K6h5a2mMuePrSAgICAgICAgICAgICAgICAgICAgICAgICAgIC0xNee6p+mHkeiejeWtpjPnj60gICAgICAgICAgICAgICAgICAgICAgICAgICAtMTXnuqfph5Hono3lraYx54+tICAgICAgICAgICAgICAgICAgICAgICAgICAgLTE157qn6YeR6J6N5a2mMuePrSAgICAgICAgICAgICAgICAgICAgICAgICAgIC0xNee6p+e7j+a1juWtpjHnj60gICAgICAgICAgICAgICAgICAgICAgICAgICAtMTXnuqfnu4/mtY7lraYy54+tICAgICAgICAgICAgICAgICAgICAgICAgICAgFSQUMjQ5ODI5NTAgICAgICAgICAgICAUMjQ5ODI5NTEgICAgICAgICAgICAUMjQ5ODI5NTIgICAgICAgICAgICAUMjQ5ODI5NTMgICAgICAgICAgICAUMjQ5ODI5NTQgICAgICAgICAgICAUMjQ5ODI5NTUgICAgICAgICAgICAUMjQ5ODI5NTVCICAgICAgICAgICAUMjQ5ODI5NTVDICAgICAgICAgICAUMjQ5ODI2NDMgICAgICAgICAgICAUMjQ5ODI2NDQgICAgICAgICAgICAUMjQ5ODI2NDUgICAgICAgICAgICAUMjQ5ODI2NDYgICAgICAgICAgICAUMjQ5ODI2NDcgICAgICAgICAgICAUMjQ5ODI4NjQgICAgICAgICAgICAUMjQ5ODI4NjUgICAgICAgICAgICAUMjQ5ODI4NjYgICAgICAgICAgICAUMjQ5ODI4NjcgICAgICAgICAgICAUMjQ5ODI4NjggICAgICAg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JlVzZXJUeXBlPVN0dWRlbnQmVXNlck51bT0yMDE4MjY4MDMwNDUnKSI+6K++6KGoPC9hPmQCBg9kFgJmDxUDTyA8YSBocmVmPSJqYXZhc2NyaXB0Ok9wZW5XaW5kb3coJ1hmel9Dai5hc2N4JlVzZXJOdW09MjAxODI2ODAzMDQ1JykiPuaIkOe7qTwvYT5cIDxhIHRhcmdldD1fYmxhbmsgaHJlZj0iLi4vTXlDb250cm9sL1N0dWRlbnRfTXlSZXBvcnQuYXNweD94aD0yMDE4MjY4MDMwNDUiPuaIkOe7qeWIhuaekDwvYT5oIDxhIGhyZWY9ImphdmFzY3JpcHQ6T3BlbldpbmRvdygnWGZ6X0J5c2guYXNjeCZVc2VyVHlwZT1TdHVkZW50JlVzZXJOdW09MjAxODI2ODAzMDQ1JykiPuavleS4muWuoeaguDwvYT5kAiwPZBYOZg8PFgIfAAUS6LSi5pS/6YeR6J6N5a2m6ZmiZGQCAQ8PFgIfAAUtMTjnuqfkvJrorqHlraYx54+tICAgICAgICAgICAgICAgICAgICAgICAgICAgZGQCAg8PFgIfAAUJ5p2O5b2s5b2kZGQCAw8PFgIfAAUMMjAxODI2ODAzMDQ2ZGQCBA8PFgIfAAUD5aWzZGQCBQ9kFgJmDxUDcCA8YSBocmVmPSJqYXZhc2NyaXB0Ok9wZW5XaW5kb3coJ0FsbF9TdHVkZW50SW5mb3IuYXNjeCZVc2VyVHlwZT1TdHVkZW50JlVzZXJOdW09MjAxODI2ODAzMDQ2JykiPuWfuuacrOS/oeaBrzwvYT5qIDxhIGhyZWY9ImphdmFzY3JpcHQ6T3BlbldpbmRvdygnTWFpbF9SZXBseS5hc2N4JlVzZXJUeXBlPVN0dWRlbnQmVXNlck51bT0yMDE4MjY4MDMwNDYnKSI+5Y+R6YCB55+t5L+hPC9hPmEgPGEgaHJlZj0iamF2YXNjcmlwdDpPcGVuV2luZG93KCdYZnpfS2NiLmFzY3gmVXNlclR5cGU9U3R1ZGVudCZVc2VyTnVtPTIwMTgyNjgwMzA0NicpIj7or77ooag8L2E+ZAIGD2QWAmYPFQNPIDxhIGhyZWY9ImphdmFzY3JpcHQ6T3BlbldpbmRvdygnWGZ6X0NqLmFzY3gmVXNlck51bT0yMDE4MjY4MDMwNDYnKSI+5oiQ57upPC9hPlwgPGEgdGFyZ2V0PV9ibGFuayBocmVmPSIuLi9NeUNvbnRyb2wvU3R1ZGVudF9NeVJlcG9ydC5hc3B4P3hoPTIwMTgyNjgwMzA0NiI+5oiQ57up5YiG5p6QPC9hPmggPGEgaHJlZj0iamF2YXNjcmlwdDpPcGVuV2luZG93KCdYZnpfQnlzaC5hc2N4JlVzZXJUeXBlPVN0dWRlbnQmVXNlck51bT0yMDE4MjY4MDMwNDYnKSI+5q+V5Lia5a6h5qC4PC9hPmRkuQjPxNuk2yJZQoaHueoNbL4xNJ6Kfy+sVGeGr6smKxc=
            __EVENTVALIDATION: /wEWRgKj2Zj1CQKKhuW9AQKEtvjxDAK8l9n5DAKvn7i0CQKD18fPDgL77rqrDQL77paYDQKl6pKVDQK57bqrDQLa7YacDQL77r6uDQL77p6WDQL77pKVDQKp7c5GAtrtmpMNApjshpwNAqXqnpYNAtrtuqsNArntgpkNAvvujpoNAvvuhpwNAtrtipcNAvvugpkNAtrtjpoNAtrtgpkNAtrtkpUNAtrtnpYNAvvumpMNArntvq4NAvvuipcNAtrtlpgNAtrtvq4NAqL62acMAoflw5wDArnTw+QEAqL6zd0LAvOB784HArnTt50EAtuCvZ0EAtiKvZ0EAqO01NUNAvD7+cYJAr6N3pIGAo/R44cCAtXiy9MOArSEnpoKAoLW5uYGAtOdiNsCApmv0KcPApuw0P4MAqbt4aIHAuy+xo4EAu6c0acMAtOH25wDAv/WrYcPAuDBl/wFApimuakKAv3Qo54BAoG09NgHAure/rEOAu2+wukNAu+c7Z4GAoHb+v0KAq2HuoAEAuHTrO0MAsr6lsIDAoPh0NELArXP0LkNAubhijODG4pLJD6NYLlNa5PoXNvd1Ns7SIMyUszu9Uvg32Sp2Q==
            _ctl1:rbtType: College
            _ctl1:ddlCollege: 68000   
            _ctl1:ddlClass: 24982950            
            _ctl1:btnSearch: 查询
    
            '''

            data = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': hid_data[0],
                '__EVENTVALIDATION': hid_data[1],
                '_ctl1:rbtType': 'College',
                '_ctl1:ddlCollege': colloge_code,
                '_ctl1:ddlClass': '24982950            ',
                '_ctl1:btnSearch': u'查询'
            }
            wb_data = self.__s.post(url=url, data=data)
            soup = BeautifulSoup(wb_data.text, 'lxml')
            options=soup.select('#_ctl1_ddlClass > option')
            for op in options:
                post_code=op.get('value')
                name=op.get_text().strip()
                data={
                    'id':post_code.strip(),
                    'post_code':post_code,
                    'name':name,
                    'colloge':Colloge.objects.get(id=colloge_code.strip()),
                    'grade':self.__clena_grade(name)
                }
                self.__ClassToObject(data=data)
                print(data)

            # print(soup)
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_one_colloge_classes timeout, retrying。。')
                return self.get_one_colloge_classes(colloge_code=colloge_code,limit_time=limit_ti, timeout=timeout)
            else:
                return None


    def get_class(self,id=['37000','450','81000']):
        colloges=Colloge.objects.all()
        for co in colloges:
            if co.id not in id:
                self.get_one_colloge_classes(co.post_code)
            else:
                pass
            # options = soup.select('#_ctl1_ddlCollege > option')


    def __get_start_student_hid(self, colloge_code='46000   ', limit_time=10, timeout=6):
        try:
            url = r'http://jwc.jxnu.edu.cn/User/default.aspx?&&code=119&uctl=MyControl%5call_searchstudent.ascx'
            # hid_data = self.__get_hid_data(url)
            hid_data = self.__get_start_class_hid()

            data = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': hid_data[0],
                '__EVENTVALIDATION': hid_data[1],
                '_ctl1:rbtType': 'College',
                '_ctl1:ddlCollege': colloge_code,
                '_ctl1:ddlClass': '24982950            ',
                '_ctl1:btnSearch': u'查询'
            }
            wb_data = self.__s.post(url=url, data=data)
            soup = BeautifulSoup(wb_data.text, 'lxml')
            __VIEWSTATE = soup.select('input[id="__VIEWSTATE"]')
            __EVENTVALIDATION = soup.select('input[id="__EVENTVALIDATION"]')
            return __VIEWSTATE[0].get('value'), __EVENTVALIDATION[0].get('value')
            # print(soup)
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('__get_start_student_hid timeout, retrying。。')
                return self.__get_start_student_hid(colloge_code=colloge_code, limit_time=limit_ti, timeout=timeout)
            else:
                return None

    def __StudentToObject(self,data):
        stu=Student()
        stu.id=data['id']
        stu.name=data['name']
        stu.gender=data['gender']
        stu.cla=data['class']
        try:
            stu.save()
        except:
            print('student exsit')


    def get_one_class_students(self,colloge_post_code,class_post_code,limit_time=10,timeout=6):
        try:
            hid = self.__get_start_student_hid(colloge_code=colloge_post_code)
            url=r'http://jwc.jxnu.edu.cn/User/default.aspx?&&code=119&uctl=MyControl%5call_searchstudent.ascx'
            data={
                '__EVENTTARGET':'',
                '__EVENTARGUMENT':'',
                '__LASTFOCUS':'',
                '__VIEWSTATE':hid[0],
                '__EVENTVALIDATION':hid[1],
                '_ctl1:rbtType':'College',
                '_ctl1:ddlCollege':colloge_post_code,
                '_ctl1:ddlClass':class_post_code,
                '_ctl1:btnSearch':'查询',
            }
            wb_data=self.__s.post(url=url,data=data,timeout=timeout)
            # print(wb_data)
            soup=BeautifulSoup(wb_data.text,'html5lib')
            li=soup.select('#_ctl1_lblMsg > li')[0]
            if li.get_text().split('：')[1].split('条')[0].strip()!='0':
                stus = soup.select('''tr[onmouseout="this.style.backgroundColor='#FFFFFF'"]''')
                try:
                    cl=Class.objects.get(id=class_post_code.strip())
                except:
                    cl=None
                for stu in stus:
                    st = stu.select('td')
                    id = st[3].get_text().strip()
                    data={
                        'id':id,
                        'name':st[2].get_text().strip(),
                        'class':cl,
                        'gender':'male' if st[4].get_text().strip()=='男' else 'female'
                    }
                    self.__StudentToObject(data)
                    print(data)
            else:
                return None
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_one_class_students timeout, retrying。。')
                return self.get_one_class_students(colloge_post_code=colloge_post_code,class_post_code=class_post_code, limit_time=limit_ti, timeout=timeout)
            else:
                return None

    def __MajorToObject(self,data):
        major=Major()
        major.major_id=data['major_id']
        major.post_code=data['post_code']
        major.grade=data['grade']
        major.name=data['name']
        major.training_objectives=data['training_objectives']
        # major.basic_knowledge=data['basic_knowledge'].encode('utf-8')
        # major.major_knowledge=data['major_knowledge'].encode('utf-8')
        major.direction_introduction=data['direction_introduction']
        major.subject=data['subject']
        major.main_subject=data['main_subject']
        major.similar_major=data['similar_major']
        major.education_background=data['education_background']
        major.degree=data['degree']
        major.length_of_schooling=data['length_of_schooling']
        major.minimum_graduation_credit=data['minimum_graduation_credit']
        major.if_multiple_directions=data['if_multiple_directions']
        try:
            major.save()
        except:
            print('major exist')
        return major


    def create_lesson_object(self,lesson_id,limit_time=5,timeout=3):
        try:
            url=r'http://jwc.jxnu.edu.cn/User/default.aspx?&&code=116&uctl=MyControl%5call_coursesearch.ascx'
            hid=self.__get_hid_data(url=url)
            data={
                '__EVENTTARGET':'',
                '__EVENTARGUMENT':'',
                '__VIEWSTATE':hid[0],
                '__EVENTVALIDATION':hid[1],
                '_ctl1:key_word':lesson_id,
                '_ctl1:key_type':'kch',
                '_ctl1:search_type':'1',
                '_ctl1:ok':'查 询',
            }
            wb_data=self.__s.post(url=url,data=data,timeout=timeout)
            soup=BeautifulSoup(wb_data.text,'html5lib')
            result=soup.select('tr[bgcolor="#F9F9F9"] > .Big')[0]
            credit=int(result.get_text().strip())
            lesson_name=soup.select('table[width="100%"] table[border="1"] > tbody > tr:nth-of-type(1) > td:nth-of-type(4)')[0].get_text().strip()
            lesson=Lesson(id=lesson_id,name=lesson_name,credit=credit)
            try:
                lesson.save()
            except:
                print(lesson_id+' 课程号已存在')
            return lesson
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('create_lesson_object timeout, retrying。。')
                return self.create_lesson_object(lesson_id=lesson_id,limit_time=limit_ti)
            else:
                return None


    def __MajorLessonToObject(self,data):
        major_lesson=MajorLesson()
        major_lesson.major=data['major']
        try:
            lesson=Lesson.objects.get(id=data['lesson_id'])
        except:
            lesson=Lesson(id=data['lesson_id'],name=data['lesson_name'],credit=data['lesson_credit'])
            lesson.save()
            # lesson=self.create_lesson_object(lesson_id=data['lesson_id'])
        major_lesson.lesson=lesson
        major_lesson.lesson_type=data['lesson_type']
        try:
            major_lesson.major_directions=data['major_directions']
        except:
            pass
        major_lesson.if_degree=data['if_degree']
        try:
            major_lesson.save()
        except:
            print(str(data['major'].name) + str(data['lesson_id']) + ' exist')


    def get_student(self):
        classes=Class.objects.all()
        for cla in classes:
            self.get_one_class_students(colloge_post_code=cla.colloge.post_code,class_post_code=cla.post_code)


    def get_one_grade_one_major(self,grade,major,limit_time=5,timeout=3):
        try:
            url=r'http://jwc.jxnu.edu.cn/User/default.aspx?&code=104&&uctl=MyControl\all_jxjh.ascx'
            hid=self.__get_hid_data(url=url)
            gra = int(grade.split('/')[0][2:])
            form_data = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': hid[0],
                '__EVENTVALIDATION': hid[1],
                '_ctl1:Nianji': grade,
                '_ctl1:zhuanye': major['post_code'],
                '_ctl1:GoSearch': '查询'
            }
            web_data = self.__s.post(url=url, data=form_data,timeout=timeout)
            web_data = web_data.text.replace('<br />', '').replace('<br>', '').replace('<br/>', '')
            # print(web_data)
            soup = BeautifulSoup(web_data, 'html5lib')
            try:
                trs = soup.select('table[width="98%"] > tbody > tr:nth-of-type(2) > td > table > tbody > tr:nth-of-type(3) > td > table > tbody > tr')
                training_objectives = trs[0].select('td')[1].get_text().strip()
                bs = trs[1].select('td:nth-of-type(2) > b')
                basic_knowledge = str(bs[0].nextSibling).strip().replace('\n', '').replace(' ', '').replace('\xa0','')
                major_knowledge = str(bs[1].nextSibling).strip().replace('\n', '').replace(' ', '').replace('\xa0','')
                major_direction_introduction = trs[2].select('td')[1].get_text().strip()
                major_type = trs[3].select('td')[1].get_text().strip()
                main_subject = trs[4].select('td')[1].get_text().strip()
                similar_major = trs[5].select('td')[1].get_text().strip()
                tds = trs[6].select('td')
                education_background = tds[1].get_text().strip()
                try:
                    length_of_schooling = int(tds[3].get_text().strip().strip('年').strip())
                except:
                    length_of_schooling = 4
                degree = tds[5].get_text().strip()
                try:
                    minimum_graduation_credit = int(tds[7].get_text().strip())
                except:
                    minimum_graduation_credit = 160
                # major_data = {
                #     'uck_grade': gra,
                #     'major_id': major['major_id'],
                #     'uck_major_name': major['major_name'],
                #     'training_objectives': None if training_objectives == '' else training_objectives,
                #     'basic_knowledge': None if basic_knowledge[1:-2] == ['', '', ''] else basic_knowledge[1:-2],
                #     'major_knowledge': None if major_knowledge[1:-2] == ['', ''] else major_knowledge[1:-2],
                #     'major_direction_introduction': major_direction_introduction,
                #     'major_type': major_type,
                #     'main_subject': main_subject,
                #     'similar_major': similar_major,
                #     'education_background': education_background,
                #     'length_of_schooling': length_of_schooling,
                #     'degree': degree,
                #     'minimum_graduation_credit': minimum_graduation_credit,
                # }
                lis = soup.select('table[width="98%"] > tbody > tr:nth-of-type(6) > td > li')
                data={
                    'major_id':major['post_code'].strip(),
                    'post_code':major['post_code'],
                    'grade':gra,
                    'name':major['major_name'].strip(),
                    'training_objectives':training_objectives,
                    # 'basic_knowledge':basic_knowledge,
                    # 'major_knowledge':major_knowledge,
                    'direction_introduction':major_direction_introduction,
                    'subject':major_type,
                    'main_subject':main_subject,
                    'similar_major':similar_major,
                    'education_background':education_background,
                    'degree':degree,
                    'length_of_schooling':length_of_schooling,
                    'minimum_graduation_credit':minimum_graduation_credit,
                    'if_multiple_directions':True if len(lis)>1 else False,
                }
                print(data)
                the_major=self.__MajorToObject(data)
                tbodys = soup.select('table[width="98%"] > tbody > tr:nth-of-type(4) > td > table > tbody')
                try:
                    for tbody in tbodys:
                        trs = tbody.select('tr')
                        # trs=trs.pop(0)
                        for tr in trs[1:]:
                            tds = tr.select('td')
                            try:
                                lesson_credit = int(tds[5].get_text().strip())
                            except:
                                lesson_credit = 2
                            # try:
                            #     lesson_quantity_a_week = int(tds[6].get_text().strip())
                            # except:
                            #     lesson_quantity_a_week = 0
                            # try:
                            #     experiment_quantity_a_week = int(tds[7].get_text().strip())
                            # except:
                            #     experiment_quantity_a_week = 0
                            # try:
                            #     lesson_quantity_all = int(tds[8].get_text().strip())
                            # except:
                            #     lesson_quantity_all = 0
                            # try:
                            #     experiment_quantity_all = int(tds[9].get_text().strip())
                            # except:
                            #     experiment_quantity_all = 0
                            # try:
                            #     lesson_turn = int(tds[10].get_text().strip().strip('第').strip('学期'))
                            # except:
                            #     lesson_turn = 0
                            # before_learning = tds[4].get_text().strip()
                            # if before_learning != '' and before_learning != '无':
                            #     bl = before_learning
                            # else:
                            #     bl = None
                            # general_course_data = {
                            #     'uck_grade': gra,
                            #     'uck_major': major['major_name'],
                            #     'lesson_type': tds[0].get_text().strip(),
                            #     'uck_lesson_id': tds[1].get_text().strip(),
                            #     'lesson_name': tds[2].get_text().strip(),
                            #     'if_degree_lesson': True if tds[3].get_text().strip() == '是' else False,
                            #     'before_learning': bl,
                            #     'lesson_credit': lesson_credit,
                            #     'week_lesson_quantity': lesson_quantity_a_week,
                            #     'week_experiment_quantity': experiment_quantity_a_week,
                            #     'all_lesson_quantity': lesson_quantity_all,
                            #     'all_experiment_quantity': experiment_quantity_all,
                            #     'lesson_turn': lesson_turn
                            # }
                            lesson_name=tds[2].get_text().strip(),
                            lesson_type=tds[0].get_text().strip()
                            if lesson_type=='公共必修':
                                lesson_type=1
                            elif lesson_type=='学科基础':
                                lesson_type=2
                            elif lesson_type=='专业主干':
                                lesson_type=3
                            else:
                                lesson_type=4
                            data={
                                'major':the_major,
                                'lesson_id':tds[1].get_text().strip(),
                                'lesson_type':lesson_type,
                                'if_degree':True if tds[3].get_text().strip() == '是' else False,
                                'lesson_name':lesson_name,
                                'lesson_credit':lesson_credit,
                            }
                            print(data)
                            self.__MajorLessonToObject(data)
                except:
                    pass

                try:
                    tbodys = soup.select('table[width="98%"] > tbody > tr:nth-of-type(6) > td > table > tbody')

                    # lisss = []
                    for tbody, li in zip(tbodys, lis):
                        trs = tbody.select('tr')
                        # less_list = []
                        # try:
                        #     minimum_credit = int(
                        #         str(li.nextSibling).strip().strip('在下列课程中至少应选修').strip('学分').strip())
                        # except:
                        #     minimum_credit = None
                        uck_major_direction = li.get_text().strip().strip('主修：').strip()
                        if uck_major_direction != '':
                            pass
                        else:
                            uck_major_direction = None
                        for tr in trs[1:]:
                            tds = tr.select('td')
                            try:
                                lesson_credit = int(tds[4].get_text().strip())
                            except:
                                lesson_credit = 2
                            # try:
                            #     lesson_quantity_a_week = int(tds[5].get_text().strip())
                            # except:
                            #     lesson_quantity_a_week = 0
                            # try:
                            #     experiment_quantity_a_week = int(tds[6].get_text().strip())
                            # except:
                            #     experiment_quantity_a_week = 0
                            # try:
                            #     lesson_quantity_all = int(tds[7].get_text().strip())
                            # except:
                            #     lesson_quantity_all = 0
                            # try:
                            #     experiment_quantity_all = int(tds[8].get_text().strip())
                            # except:
                            #     experiment_quantity_all = 0
                            # try:
                            #     lesson_turn = int(tds[9].get_text().strip().strip('第').strip('学期'))
                            # except:
                            #     lesson_turn = 0
                            # before_learn = tds[3].get_text().strip()
                            # if before_learn != '' and before_learn != '无':
                            #     bl = before_learn
                            # else:
                            #     bl = None
                            # limit_course_data = {
                            #     'uck_lesson_id': tds[1].get_text().strip(),
                            #     'lesson_name': tds[2].get_text().strip(),
                            #     'before_learning': bl,
                            #     'lesson_credit': lesson_credit,
                            #     'week_lesson_quantity': lesson_quantity_a_week,
                            #     'week_experiment_quantity': experiment_quantity_a_week,
                            #     'all_lesson_quantity': lesson_quantity_all,
                            #     'all_experiment_quantity': experiment_quantity_all,
                            #     'lesson_turn': lesson_turn
                            # }
                            # less_list.append(limit_course_data)
                            if the_major.if_multiple_directions==True:
                                data = {
                                    'major': the_major,
                                    'lesson_id': tds[1].get_text().strip(),
                                    'lesson_type': 5,
                                    'if_degree': False,
                                    'major_directions':uck_major_direction,
                                    'lesson_credit':lesson_credit,
                                    'lesson_name':tds[2].get_text().strip(),
                                }
                                print(data)
                                self.__MajorLessonToObject(data)
                            else:
                                data = {
                                    'major': the_major,
                                    'lesson_id': tds[1].get_text().strip(),
                                    'lesson_type': 5,
                                    'if_degree': False,
                                    'lesson_credit': lesson_credit,
                                    'lesson_name': tds[2].get_text().strip(),
                                }
                                print(data)
                                self.__MajorLessonToObject(data)
                except:
                    pass
            except:
                pass
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_one_grade_one_major timeout, retrying。。')
                return self.get_one_grade_one_major(grade=grade,major=major,limit_time=limit_ti)
            else:
                return None


    def get_major(self):
        url = r'http://jwc.jxnu.edu.cn/User/default.aspx?&code=104&&uctl=MyControl\all_jxjh.ascx'
        # hid_data=self.get_hid_data(url)
        wb_data = self.__s.get(url)
        soup = BeautifulSoup(wb_data.text, 'lxml')
        # __VIEWSTATE = soup.select('input[name="__VIEWSTATE"]')[0].get('value')
        # __EVENTVALIDATION = soup.select('input[name="__EVENTVALIDATION"]')[0].get('value')
        majors = soup.select('#_ctl1_zhuanye > option')
        for major in majors:
            post_code = major.get('value')
            maj = major.get_text().strip()
            major={
                'post_code':post_code,
                'major_name':maj,
            }
            grade_list = GRADE_LIST
            # print(major_id)
            for grade in grade_list:
                self.get_one_grade_one_major(grade=grade,major=major)


if __name__ == '__main__':
    spd=SpiderStaticStudent('201626703079','m19980220')
    spd.sign_in(limit_time=20)
    # spd.get_colloges()
    # spd.get_class()
    # spd.get_one_colloge_classes(colloge_code='57000   ')
    # spd.get_one_class_students(colloge_post_code='49000   ',class_post_code='24982425A           ')
    # spd.get_student()
    # spd.get_one_grade_one_major('2018/9/1 0:00:00',{'post_code':'130101W ','major_name':'表演（戏剧影视）'})
    spd.get_major()








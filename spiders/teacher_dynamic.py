#-*- coding:utf-8 -*-

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
django.setup()

from jwxzs_2.settings import VERIFICATIONCODE_SRC

from utils.settings import MY_USERNAME,MY_WORD

import requests
from bs4 import BeautifulSoup
from PIL import Image
from pytesseract import pytesseract
# import tesserocr
import uuid,os,time
from users.models import Colloge,Class,Student,Major,StudentDetail,UserProfile
from scores.models import TotalCredit,Score
from lessons.models import MajorLesson,ScheduleLesson
import random

class SpiderDynamicTeacher:
    def __init__(self,id,password):
        self.id=id
        self.password=password
        self.__s=requests.Session()

    # get方法请求，获得隐藏参数 viewstate、eventvalidation
    def __get_hid_data(self, url, error_time_limit=10,timeout=4):
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
    def __get_hid_data_and_vecode(self,url,error_time_limit=3,timeout=2):
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
                return None

    #验证码识别
    def verification_code(self):
        try:
            print('verification_code is working。。')
            url1 = 'http://jwc.jxnu.edu.cn/Portal/LoginAccount.aspx?t=account'
            hid=self.__get_hid_data_and_vecode(url=url1)
            src=VERIFICATIONCODE_SRC+hid[2]
            # print(src)
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
            # result=pytesseract.image_to_string(pppp)
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
    # def sign_in(self,limit_time=10,timeout=4):
    #     try:
    #         url1 = 'http://jwc.jxnu.edu.cn/Portal/LoginAccount.aspx?t=account'
    #         hid= self.verification_code()
    #         #登录表单
    #         data1={
    #             '__VIEWSTATE':hid[0],
    #             '__EVENTVALIDATION':hid[1],
    #             '_ctl0:cphContent:ddlUserType':'Teacher',
    #             '_ctl0:cphContent:txtUserNum':self.id,
    #             '_ctl0:cphContent:txtPassword':self.password,
    #             '_ctl0:cphContent:btnLogin':'登录',
    #             '_ctl0:cphContent:txtCheckCode':hid[2],
    #         }
    #         b=self.__s.post(url1,data=data1,timeout=timeout)
    #         soup=BeautifulSoup(b.text,'html5lib')
    #         # print(soup)
    #         jwtz=soup.select('#jwtz')
    #         # print(jwtz)
    #         if jwtz!=[]:
    #             print('sign in successfluly!')
    #             return 1
    #         else:
    #             limit_t=limit_time-1
    #             print('sign in fail')
    #             if limit_t>0:
    #                 time.sleep(1)
    #                 print('sign_in failed, retrying。。')
    #                 return self.sign_in(limit_time=limit_t,timeout=timeout)
    #             else:
    #                 return None
    #             # print(b.text)
    #     except:
    #         limit_ti=limit_time-1
    #         if limit_ti > 0:
    #             print('sign_in timeout, retrying。。')
    #             return self.sign_in(limit_time=limit_ti,timeout=timeout)
    #         else:
    #             print(self.id)
    #             print(self.password)
    #             return None

    def sign_in(self,limit_time=10,timeout=5):
        try:
            url = 'http://jwc.jxnu.edu.cn/Portal/LoginAccount.aspx?t=account'
            data = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': '/wEPDwUJNjA5MzAzMTcwD2QWAmYPZBYCAgMPZBYGZg8WAh4EVGV4dAUgMjAxOeW5tDTmnIgxM+aXpSDmmJ/mnJ/lha0mbmJzcDtkAgIPZBYCAgEPFgIfAAUS6LSm5Y+35a+G56CB55m75b2VZAIDD2QWBAIBDw8WAh4HVmlzaWJsZWdkFgoCAQ8QZGQWAWZkAgMPZBYCAgEPFgIfAAUG5a2m5Y+3ZAIFDw8WAh8BaGQWAgIBDxAPFgYeDURhdGFUZXh0RmllbGQFDOWNleS9jeWQjeensB4ORGF0YVZhbHVlRmllbGQFCeWNleS9jeWPtx4LXyFEYXRhQm91bmRnZBAVGxLotKLmlL/ph5Hono3lrabpmaIS5Z+O5biC5bu66K6+5a2m6ZmiEuWIneetieaVmeiCsuWtpumZohXlnLDnkIbkuI7njq/looPlrabpmaIS5YWs6LS55biI6IyD55Sf6ZmiEuWbvemZheaVmeiCsuWtpumZohLljJblrabljJblt6XlrabpmaIb6K6h566X5py65L+h5oGv5bel56iL5a2m6ZmiEue7p+e7reaVmeiCsuWtpumZogzmlZnogrLlrabpmaIe5Yab5LqL5pWZ56CU6YOo77yI5q2m6KOF6YOo77yJEuenkeWtpuaKgOacr+WtpumZohvljoblj7LmlofljJbkuI7ml4XmuLjlrabpmaIV6ams5YWL5oCd5Li75LmJ5a2m6ZmiDOe+juacr+WtpumZogzova/ku7blrabpmaIJ5ZWG5a2m6ZmiEueUn+WRveenkeWtpuWtpumZohvmlbDlrabkuI7kv6Hmga/np5HlrablrabpmaIM5L2T6IKy5a2m6ZmiD+WkluWbveivreWtpumZognmloflrabpmaIb54mp55CG5LiO6YCa5L+h55S15a2Q5a2m6ZmiDOW/g+eQhuWtpumZohXmlrDpl7vkuI7kvKDmkq3lrabpmaIM6Z+z5LmQ5a2m6ZmiDOaUv+azleWtpumZohUbCDY4MDAwICAgCDYzMDAwICAgCDgyMDAwICAgCDQ4MDAwICAgCDU3MDAwICAgCDY5MDAwICAgCDYxMDAwICAgCDYyMDAwICAgCDQ1MCAgICAgCDUwMDAwICAgCDM3MDAwICAgCDgxMDAwICAgCDU4MDAwICAgCDQ2MDAwICAgCDY1MDAwICAgCDY3MDAwICAgCDU0MDAwICAgCDY2MDAwICAgCDU1MDAwICAgCDU2MDAwICAgCDUyMDAwICAgCDUxMDAwICAgCDYwMDAwICAgCDQ5MDAwICAgCDY0MDAwICAgCDUzMDAwICAgCDU5MDAwICAgFCsDG2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZxYBZmQCCw8PFgIeCEltYWdlVXJsBSRjaGVja2NvZGUuYXNweD9jb2RlPUEwRDM0OTkyRTY0QTA4QTlkZAINDxYCHwAFEEEwRDM0OTkyRTY0QTA4QTlkAgMPDxYCHwFoZGRkVKkChFZpdlQPdlHy2JNRlch/myJywKCzK0eOTM5tgKI=',
                '__EVENTVALIDATION': '/wEWCgL+uuD+AgKFsp/HCgL+44ewDwKiwZ6GAgKWuv6KDwLj3Z22BgL6up5fAv/WopgDAqbyykwC68zH9gaIVcuoN2ppvvS2+yQJvvk3Fl/uM/vu9jcD1EIn80deUg==',
                '_ctl0:cphContent:ddlUserType': 'Teacher',
                '_ctl0:cphContent:txtUserNum': self.id,
                '_ctl0:cphContent:txtPassword': self.password,
                '_ctl0:cphContent:txtCheckCode': 'YUN3',
                '_ctl0:cphContent:btnLogin': '登录'
            }
            wb_data = self.__s.post(url=url, data=data, timeout=timeout)
            soup = BeautifulSoup(wb_data.text, 'html5lib')
            jwtz = soup.select('#jwtz')
            if jwtz != []:
                print('sign in successfluly!')
                return True
            else:
                limit_t = limit_time - 1
                print('sign in fail')
                if limit_t > 0:
                    time.sleep(1)
                    print('sign_in failed, retrying。。')
                    return self.sign_in(limit_time=limit_t, timeout=timeout)
                else:
                    return None
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('sign_in timeout, retrying。。')
                return self.sign_in(limit_time=limit_ti, timeout=timeout)
            else:
                print(self.id)
                print(self.password)
                return None

if __name__ == '__main__':
    tea=SpiderDynamicTeacher(id='',password='')
    tea.sign_in()

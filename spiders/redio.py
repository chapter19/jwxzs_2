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
from datetime import datetime

from redio.models import Redio


class SpiderRedio:
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
    def __get_hid_data_and_vecode(self,url,ve_src,error_time_limit=3,timeout=2):
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
            src=ve_src+vecode_name
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
    def verification_code(self,ve_src):
        try:
            print('verification_code is working。。')
            url1 = 'http://jwc.jxnu.edu.cn/Portal/LoginAccount.aspx?t=account'
            hid=self.__get_hid_data_and_vecode(url=url1,ve_src=ve_src)
            src=ve_src+hid[2]
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
    # def sign_in(self,ve_src=VERIFICATIONCODE_SRC,limit_time=10,timeout=4):
    #     try:
    #         url1 = 'http://jwc.jxnu.edu.cn/Portal/LoginAccount.aspx?t=account'
    #         hid= self.verification_code(ve_src=ve_src)
    #         #登录表单
    #         data1={
    #             '__VIEWSTATE':hid[0],
    #             '__EVENTVALIDATION':hid[1],
    #             '_ctl0:cphContent:ddlUserType':'Student',
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

    def sign_in(self,limit_time=10,timeout=4):
        try:
            url='http://jwc.jxnu.edu.cn/Portal/LoginAccount.aspx?t=account'
            data={
                '__EVENTTARGET':'',
                '__EVENTARGUMENT':'',
                '__LASTFOCUS':'',
                '__VIEWSTATE':'/wEPDwUJNjA5MzAzMTcwD2QWAmYPZBYCAgMPZBYGZg8WAh4EVGV4dAUgMjAxOeW5tDTmnIgxM+aXpSDmmJ/mnJ/lha0mbmJzcDtkAgIPZBYCAgEPFgIfAAUS6LSm5Y+35a+G56CB55m75b2VZAIDD2QWBAIBDw8WAh4HVmlzaWJsZWdkFgoCAQ8QZGQWAWZkAgMPZBYCAgEPFgIfAAUG5a2m5Y+3ZAIFDw8WAh8BaGQWAgIBDxAPFgYeDURhdGFUZXh0RmllbGQFDOWNleS9jeWQjeensB4ORGF0YVZhbHVlRmllbGQFCeWNleS9jeWPtx4LXyFEYXRhQm91bmRnZBAVGxLotKLmlL/ph5Hono3lrabpmaIS5Z+O5biC5bu66K6+5a2m6ZmiEuWIneetieaVmeiCsuWtpumZohXlnLDnkIbkuI7njq/looPlrabpmaIS5YWs6LS55biI6IyD55Sf6ZmiEuWbvemZheaVmeiCsuWtpumZohLljJblrabljJblt6XlrabpmaIb6K6h566X5py65L+h5oGv5bel56iL5a2m6ZmiEue7p+e7reaVmeiCsuWtpumZogzmlZnogrLlrabpmaIe5Yab5LqL5pWZ56CU6YOo77yI5q2m6KOF6YOo77yJEuenkeWtpuaKgOacr+WtpumZohvljoblj7LmlofljJbkuI7ml4XmuLjlrabpmaIV6ams5YWL5oCd5Li75LmJ5a2m6ZmiDOe+juacr+WtpumZogzova/ku7blrabpmaIJ5ZWG5a2m6ZmiEueUn+WRveenkeWtpuWtpumZohvmlbDlrabkuI7kv6Hmga/np5HlrablrabpmaIM5L2T6IKy5a2m6ZmiD+WkluWbveivreWtpumZognmloflrabpmaIb54mp55CG5LiO6YCa5L+h55S15a2Q5a2m6ZmiDOW/g+eQhuWtpumZohXmlrDpl7vkuI7kvKDmkq3lrabpmaIM6Z+z5LmQ5a2m6ZmiDOaUv+azleWtpumZohUbCDY4MDAwICAgCDYzMDAwICAgCDgyMDAwICAgCDQ4MDAwICAgCDU3MDAwICAgCDY5MDAwICAgCDYxMDAwICAgCDYyMDAwICAgCDQ1MCAgICAgCDUwMDAwICAgCDM3MDAwICAgCDgxMDAwICAgCDU4MDAwICAgCDQ2MDAwICAgCDY1MDAwICAgCDY3MDAwICAgCDU0MDAwICAgCDY2MDAwICAgCDU1MDAwICAgCDU2MDAwICAgCDUyMDAwICAgCDUxMDAwICAgCDYwMDAwICAgCDQ5MDAwICAgCDY0MDAwICAgCDUzMDAwICAgCDU5MDAwICAgFCsDG2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZxYBZmQCCw8PFgIeCEltYWdlVXJsBSRjaGVja2NvZGUuYXNweD9jb2RlPUEwRDM0OTkyRTY0QTA4QTlkZAINDxYCHwAFEEEwRDM0OTkyRTY0QTA4QTlkAgMPDxYCHwFoZGRkVKkChFZpdlQPdlHy2JNRlch/myJywKCzK0eOTM5tgKI=',
                '__EVENTVALIDATION':'/wEWCgL+uuD+AgKFsp/HCgL+44ewDwKiwZ6GAgKWuv6KDwLj3Z22BgL6up5fAv/WopgDAqbyykwC68zH9gaIVcuoN2ppvvS2+yQJvvk3Fl/uM/vu9jcD1EIn80deUg==',
                '_ctl0:cphContent:ddlUserType':'Student',
                '_ctl0:cphContent:txtUserNum':self.id,
                '_ctl0:cphContent:txtPassword':self.password,
                '_ctl0:cphContent:txtCheckCode':'YUN3',
                '_ctl0:cphContent:btnLogin':'登录'
            }
            wb_data=self.__s.post(url=url,data=data,timeout=timeout)
            soup=BeautifulSoup(wb_data.text,'html5lib')
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



    def get_redio_GongGao(self,page_start=1,page_end=3):
        urls=['http://jwc.jxnu.edu.cn/Portal/ArticlesList.aspx?type=jwgg&page=%d' % a for a in range(page_start,page_end)]
        for u in urls:
            self.get_one_page_GongGao(u)

    def get_one_page_GongGao(self,u,timeout=3,limit_time=5):
        try:
            wb_data = self.__s.get(u,timeout=timeout)
            soup = BeautifulSoup(wb_data.text, 'html5lib')
            aas = soup.select('#main-content > div > div.line > a')
            for a in aas:
                url = a.get('href')
                id = url.split('=')[-1]
                red = Redio.objects.filter(id=id)
                if not red:
                    da = a.get_text().strip()
                    try:
                        title = da.split('【')[0].strip()
                        (htm, tim) = self.get_body_GongGao(part_url=url)
                        try:
                            red = Redio.objects.create(id=id, title=title, time=tim, body=htm)
                            print(red)
                        except:
                            url = 'http://jwc.jxnu.edu.cn/Portal/' + url
                            body = '<a href="%s" target="_blank">%s</a>' % (url, title)
                            red = Redio.objects.create(id=id, title=title, time=tim, body=body)
                            print(id, title, tim)
                            print(red)
                    except:
                        url = 'http://jwc.jxnu.edu.cn/Portal/' + url
                        mess = '公告爬取异常，页码：%s，网址：%s' % (u.split('=')[-1], url)
                        print(mess)
                else:
                    print('通知已存在')
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_one_page_GongGao timeout, retrying。。')
                return self.get_one_page_GongGao(u=u,limit_time=limit_ti)
            else:
                return None


    def get_body_GongGao(self,part_url,timeout=3,limit_time=5):
        try:
            true_url='http://jwc.jxnu.edu.cn/Portal/'+part_url
            wb_data=self.__s.get(true_url,timeout=timeout)
            soup=BeautifulSoup(wb_data.text,'html5lib')
            try:
                tim=soup.select('#main-content > .text-sub')[0].get_text().strip().replace('【时间：','').replace('】','')
                htm=soup.select('#main-content > #main-content')[0]
                htm = str(htm).replace('/UploadSystem/','http://jwc.jxnu.edu.cn/UploadSystem/')
                return htm,tim
            except:
                return None
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_body_GongGao timeout, retrying。。')
                return self.get_body_GongGao(part_url=part_url,limit_time=limit_ti)
            else:
                return None


    def get_redio_TongZhi(self,page_start=1,page_end=3):
        urls = ['http://jwc.jxnu.edu.cn/Portal/ArticlesList.aspx?type=Jwtz&page=%d' % a for a in range(page_start,page_end)]
        for u in urls:
            self.get_one_page_TongZhi(u)

    def get_one_page_TongZhi(self,u,timeout=3,limit_time=5):
        try:
            wb_data = self.__s.get(u,timeout=timeout)
            soup = BeautifulSoup(wb_data.text, 'html5lib')
            aas = soup.select('#main-content > div > div.line > a')
            for a in aas:
                url = a.get('href')
                id = url.split('=')[-1]
                red = Redio.objects.filter(id=id)
                if not red:
                    da = a.get_text().strip()
                    try:
                        title = da.split('】')[1].split('【')[0].strip()
                        (htm, tim) = self.get_body_TongZhi(part_url=url)
                        red = Redio.objects.create(id=id, title=title, time=tim, body=htm)
                        print(red)
                    except:
                        mess = '公告爬取异常，页码：%s，网址：%s' % (u.split('=')[-1], url)
                        print(mess)
                else:
                    print('通知已存在')
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_one_page_TongZhi timeout, retrying。。')
                return self.get_one_page_TongZhi(u=u,limit_time=limit_ti)
            else:
                return None


    def get_body_TongZhi(self,part_url,timeout=3,limit_time=5):
        try:
            true_url='http://jwc.jxnu.edu.cn/Portal/'+part_url
            wb_data=self.__s.get(true_url,timeout=timeout)
            soup=BeautifulSoup(wb_data.text,'html5lib')
            try:
                tim=soup.select('#main-content > .text-sub')[0].get_text().strip().split('：')[-1].strip('】').strip()
                tim+=' 0:00:00'
                htm=soup.select('#main-content > #main-content')[0]
                htm = str(htm).replace('/UploadSystem/','http://jwc.jxnu.edu.cn/UploadSystem/')
                return htm,tim
            except:
                return None
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_body_TongZhi timeout, retrying。。')
                return self.get_body_TongZhi(part_url=part_url, limit_time=limit_ti)
            else:
                return None



    def test(self):
        for i in range(1,2):
            print(i)

if __name__ == '__main__':
    s=SpiderRedio(id=MY_USERNAME,password=MY_WORD)
    s.sign_in()
    # s.get_redio1(1)
    # s.get_body1(part_url='ArticlesView.aspx?id=6530')
    # s.test()
    s.get_redio_GongGao(page_start=1,page_end=168)
    # s.get_redio_TongZhi(page_start=1,page_end=184)
    # s.get_body_GongGao(part_url='ArticlesView.aspx?id=4868')
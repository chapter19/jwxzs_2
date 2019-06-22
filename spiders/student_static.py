#-*- coding:utf-8 -*-

# import os,django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
# django.setup()

# from jwxzs_2.settings import VERIFICATIONCODE_SRC
    # ,GRADE_LIST

from utils.settings import MY_WORD,MY_USERNAME

import requests
from bs4 import BeautifulSoup
from PIL import Image
# import pytesseract
import uuid,os,time
from users.models import Colloge,Class,Student,Major,UserProfile
from lessons.models import MajorLesson,Lesson
from semesters.models import Semester
from spider.models import SpiderLogDetail

from jwxzs_2.settings import PUBLIC_PASSWORD

def get_spider_grade():
    grade = Semester.objects.filter(if_spider_grade=True).values('post_code').distinct()
    # print(grade)
    return grade

class SpiderStaticStudent:
    def __init__(self,id,password):
        self.id=id
        self.password=password
        self.__s=requests.Session()
        self.grade_list=get_spider_grade()

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

    # #获取隐藏值和验证码
    # def __get_hid_data_and_vecode(self,url,error_time_limit=7,timeout=2):
    #     try:
    #         b=self.__s.get(url,timeout=timeout)
    #         soup=BeautifulSoup(b.text,'html5lib')
    #         # print(soup)
    #         __VIEWSTATE = soup.select('input[id="__VIEWSTATE"]')
    #         __EVENTVALIDATION = soup.select('input[id="__EVENTVALIDATION"]')
    #         photo_url='http://jwc.jxnu.edu.cn/Portal/'+soup.select('#_ctl0_cphContent_imgPasscode')[0].get('src')
    #         # print(photo_url)
    #         d=self.__s.get(photo_url)
    #         vecode_name=str(uuid.uuid1())+'.gif'
    #         src=VERIFICATIONCODE_SRC+vecode_name
    #         # print(__VIEWSTATE[0].get('value'),__EVENTVALIDATION[0].get('value'),vecode_name)
    #         with open(src,'wb') as vecode:
    #             vecode.write(d.content)
    #             vecode.close()
    #         return __VIEWSTATE[0].get('value'),__EVENTVALIDATION[0].get('value'),vecode_name
    #     except:
    #         error_time_limit-=1
    #         if error_time_limit>0:
    #             print('__get_hid_data_and_vecode timeout, retrying。。')
    #             return self.__get_hid_data_and_vecode(url=url,error_time_limit=error_time_limit,timeout=timeout)
    #         else:
    #             return 0
    #
    # #验证码识别
    # def verification_code(self):
    #     # try:
    #     print('verification_code is working。。')
    #     url1 = 'http://jwc.jxnu.edu.cn/Portal/LoginAccount.aspx?t=account'
    #     hid=self.__get_hid_data_and_vecode(url=url1)
    #     src=VERIFICATIONCODE_SRC+hid[2]
    #     image=Image.open(src)
    #     # x, y = image.size
    #     # p = Image.new('RGBA', image.size, (255, 255, 255))
    #     # p.paste(image, (0, 0, x, y), image)
    #     # image=image.convert('L')
    #     # threshold=80
    #     # table=[]
    #     # for i in range(256):
    #     #     if i < threshold:
    #     #         table.append(0)
    #     #     else:
    #     #         table.append(1)
    #     # image=image.point(table,'1')
    #     # w,h=image.size
    #     # ppp = Image.new('RGBA', image.size, (255, 255, 255))
    #     # ppp.paste(image, (0, 0, w, h))
    #     # iii=ppp.resize((w,h))
    #     # os.remove(src)
    #     # iii.save(src)
    #     # pppp=Image.open(src)
    #
    #     # iii=image.resize((w*2,h*2))
    #     # iii.show()
    #     result=str(pytesseract.image_to_string(image,lang='eng')).replace('.','').replace(',','').replace('(','').replace(')','').replace(':','').replace('/','').replace('[','').replace(']','').strip()
    #     os.remove(src)
    #     print(result)
    #     # new_src='./VerificationCode/'+result+'.png'
    #     # os.rename(src,new_src)
    #     # print(result)
    #     return hid[0],hid[1],result
    #     # except:
    #     #     print('verification_code failed.')
    #     #     return None

    # 登录
    # def sign_in(self,limit_time=10,timeout=5):
    #     # try:
    #     url1 = 'http://jwc.jxnu.edu.cn/Portal/LoginAccount.aspx?t=account'
    #     hid= self.verification_code()
    #     #登录表单
    #     data1={
    #         '__EVENTTARGET':'',
    #         '__EVENTARGUMENT':'',
    #         '__LASTFOCUS':'',
    #         '__VIEWSTATE':hid[0],
    #         '__EVENTVALIDATION':hid[1],
    #         '_ctl0:cphContent:ddlUserType':'Student',
    #         '_ctl0:cphContent:txtUserNum':self.id,
    #         '_ctl0:cphContent:txtPassword':self.password,
    #         '_ctl0:cphContent:btnLogin':'登录',
    #         '_ctl0:cphContent:txtCheckCode':hid[2],
    #     }
    #     b=self.__s.post(url1,data=data1,timeout=timeout)
    #     soup=BeautifulSoup(b.text,'html5lib')
    #     # print(soup)
    #     jwtz=soup.select('#jwtz')
    #     # print(jwtz)
    #     if jwtz!=[]:
    #         print('sign in successfluly!')
    #         return 1
    #     else:
    #         limit_t=limit_time-1
    #         print('sign in fail')
    #         if limit_t>0:
    #             time.sleep(1)
    #             print('sign_in failed, retrying。。')
    #             return self.sign_in(limit_time=limit_t,timeout=timeout)
    #         else:
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
                '_ctl0:cphContent:ddlUserType': 'Student',
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
                raise Exception('登录异常！')

    #插入学院
    def __CollogeToObject(self,log_id,data):
        colloge=Colloge.objects.filter(id=data['id'])
        if colloge:
            colloge=colloge[0]
            desc='{0} {1}'.format(colloge.name,colloge.id)
            SpiderLogDetail.objects.create(spider_log_id=log_id,desc=desc,model='Colloge',status='fail')
            print('colloge exsit')
        else:
            colloge=Colloge()
            colloge.id=data['id']
            colloge.name=data['name']
            colloge.post_code=data['post_code']
            colloge.save()
            desc = '{0} {1}'.format(colloge.name, colloge.id)
            SpiderLogDetail.objects.create(spider_log_id=log_id, desc=desc, model='Colloge')


    def get_colloges(self,log_id,limit_time=7,timeout=5):
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
                    self.__CollogeToObject(data=data,log_id=log_id)
                    print(data)
                except:
                    print('insert colloge already')
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_colloges timeout, retrying。。')
                return self.get_colloges(limit_time=limit_ti,timeout=timeout)
            else:
                raise Exception('爬取学院异常！')


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

    def __ClassToObject(self,data,log_id):
        cla=Class.objects.filter(id=data['id'])
        if cla:
            cla=cla[0]
            SpiderLogDetail.objects.create(spider_log_id=log_id, desc=cla.name, model='Class', status='fail')
            print('class exsit')
        else:
            cla=Class()
            cla.id=data['id']
            cla.name=data['name']
            cla.post_code=data['post_code']
            cla.colloge=data['colloge']
            cla.grade=data['grade']
            cla.save()
            SpiderLogDetail.objects.create(spider_log_id=log_id, desc=cla.name,model='Class')


    def __clena_grade(self,str):
        try:
            grade=int(str.split('级')[0].strip())
            return grade
        except:
            return None


    def get_one_colloge_classes(self,log_id,colloge_code='46000   ',limit_time=5,timeout=4):
        try:
            url = r'http://jwc.jxnu.edu.cn/User/default.aspx?&&code=119&uctl=MyControl%5call_searchstudent.ascx'
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
                self.__ClassToObject(data=data,log_id=log_id)
                print(data)

            # print(soup)
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_one_colloge_classes timeout, retrying。。')
                return self.get_one_colloge_classes(log_id=log_id,colloge_code=colloge_code,limit_time=limit_ti, timeout=timeout)
            else:
                raise Exception('爬取异常！')

    def get_one_colloge_one_grade_classes(self,grade,log_id,colloge_code='46000   ',limit_time=5,timeout=4):
        try:
            url = r'http://jwc.jxnu.edu.cn/User/default.aspx?&&code=119&uctl=MyControl%5call_searchstudent.ascx'
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
            options=soup.select('#_ctl1_ddlClass > option')
            for op in options:
                post_code=op.get('value')
                name=op.get_text().strip()
                if name[:2]==str(grade):
                    data={
                        'id':post_code.strip(),
                        'post_code':post_code,
                        'name':name,
                        'colloge':Colloge.objects.get(id=colloge_code.strip()),
                        'grade':self.__clena_grade(name)
                    }
                    self.__ClassToObject(data=data,log_id=log_id)
                    print(data)
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_one_colloge_classes timeout, retrying。。')
                return self.get_one_colloge_classes(log_id=log_id,colloge_code=colloge_code,limit_time=limit_ti, timeout=timeout)
            else:
                raise Exception('爬取异常！')

    def get_one_grade_class_from_all_colloge(self,grade,log_id):
        colloges = Colloge.objects.all()
        for co in colloges:
            if co.id not in id:
                self.get_one_colloge_one_grade_classes(grade=grade,colloge_code=co.post_code,log_id=log_id)
            else:
                pass


    def get_class_from_all_colloge(self,log_id,id=['37000','450','81000']):
        colloges=Colloge.objects.all()
        for co in colloges:
            if co.id not in id:
                self.get_one_colloge_classes(colloge_code=co.post_code,log_id=log_id)
            else:
                pass
            # options = soup.select('#_ctl1_ddlCollege > option')

    def get_class(self,colloge_post_code,log_id,if_all=False):
        if if_all:
            colloges = Colloge.objects.all()
            for co in colloges:
                if co.id not in id:
                    self.get_one_colloge_classes(colloge_code=co.post_code,log_id=log_id)
                else:
                    pass
        else:
            self.get_one_colloge_classes(colloge_post_code)


    def __get_start_student_hid(self, colloge_code='46000   ', limit_time=10, timeout=6):
        try:
            url = r'http://jwc.jxnu.edu.cn/User/default.aspx?&&code=119&uctl=MyControl%5call_searchstudent.ascx'
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
                '_ctl1:btnSearch': '查询'
            }
            wb_data = self.__s.post(url=url, data=data)
            soup = BeautifulSoup(wb_data.text, 'lxml')
            __VIEWSTATE = soup.select('input[id="__VIEWSTATE"]')
            __EVENTVALIDATION = soup.select('input[id="__EVENTVALIDATION"]')
            return __VIEWSTATE[0].get('value'), __EVENTVALIDATION[0].get('value')
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('__get_start_student_hid timeout, retrying。。')
                return self.__get_start_student_hid(colloge_code=colloge_code, limit_time=limit_ti, timeout=timeout)
            else:
                return None

    def __StudentToObject(self,data,log_id):
        stu=Student.objects.filter(id=data['id'])
        if stu:
            stu = stu[0]
            desc='{0} {1} {2}'.format(stu.cla.name,stu.name,stu.id)
            SpiderLogDetail.objects.create(spider_log_id=log_id, desc=desc, model='Student', status='fail')
            print('student exsit')
        else:
            stu=Student()
            stu.id=data['id']
            stu.name=data['name']
            stu.gender=data['gender']
            stu.cla=data['class']
            stu.save()
            if not stu.user:
                user = self.__student_create_user(stu)
                self.get_student_photo(user)
            desc = '{0} {1} {2}'.format(stu.cla.name, stu.name, stu.id)
            SpiderLogDetail.objects.create(spider_log_id=log_id, desc=desc, model='Student')

    def __student_create_user(self,stu):
        if not stu.user:
            user=UserProfile.objects.create(username=stu.id,name=stu.name,gender=stu.gender,is_student=True,is_active=False,password=PUBLIC_PASSWORD)
            return user

    def get_one_class_students(self,colloge_post_code,log_id,class_post_code,limit_time=5,timeout=5):
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
                    self.__StudentToObject(data=data,log_id=log_id)
                    print(data)
            else:
                return None
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_one_class_students timeout, retrying。。')
                return self.get_one_class_students(log_id=log_id,colloge_post_code=colloge_post_code,class_post_code=class_post_code, limit_time=limit_ti, timeout=timeout)
            else:
                raise Exception('爬取学生异常！')

    def get_colloge_grade_student(self,log_id,colloge_post_code,grade):
        if colloge_post_code=='all':
            if grade=='all':
                cla=Class.objects.all()
                for c in cla:
                    self.get_one_class_students(colloge_post_code=c.colloge.post_code,log_id=log_id,class_post_code=c.post_code)
            else:
                cla=Class.objects.filter(grade=int(grade))
                for c in cla:
                    self.get_one_class_students(colloge_post_code=c.colloge.post_code,log_id=log_id,class_post_code=c.post_code)
        else:
            colloge = Colloge.objects.filter(post_code=colloge_post_code)
            if not colloge:
                raise Exception('爬取学生异常！学院不存在！')
            else:
                colloge=colloge[0]
                if grade=='all':
                    cla=Class.objects.filter(colloge=colloge)
                    for c in cla:
                        self.get_one_class_students(colloge_post_code=colloge.post_code, log_id=log_id,class_post_code=c.post_code)
                else:
                    cla = Class.objects.filter(colloge=colloge,grade=int(grade))
                    for c in cla:
                        self.get_one_class_students(colloge_post_code=colloge.post_code, log_id=log_id,class_post_code=c.post_code)


    def __MajorToObject(self,log_id,data):
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
            desc='{0}级{1}'.format(data['grade'],data['name'])
            SpiderLogDetail.objects.create(spider_log_id=log_id,model='Major',status='success',desc=desc)
        except:
            desc = '{0}级{1}'.format(major.grade, major.name)
            SpiderLogDetail.objects.create(spider_log_id=log_id, model='Major', status='fail', desc=desc)
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


    def __MajorLessonToObject(self,log_id,data):
        #单方向专业课程是否已存在
        if data['major'].if_multiple_directions:
            major_lesson = MajorLesson.objects.filter(major=data['major'], lesson_id=data['lesson_id'],major_directions=data['major_directions'])
            if not major_lesson:
                #多方向课程该方向课程是否已存在
                    # if major_lesson:
                    #     major_lesson=MajorLesson()
                    #     major_lesson.major=data['major']
                major_lesson=MajorLesson()
                try:
                    lesson=Lesson.objects.get(id=data['lesson_id'])
                except:
                    lesson=Lesson(id=data['lesson_id'],name=data['lesson_name'],credit=data['lesson_credit'])
                    lesson.save()
                    # lesson=self.create_lesson_object(lesson_id=data['lesson_id'])
                major_lesson.lesson=lesson
                major_lesson.major = data['major']
                major_lesson.lesson_type=data['lesson_type']
                major_lesson.open_semester=data['open_semester']
                major_lesson.limit_lesson_minimum_credit=data['limit_lesson_minimum_credit']
                try:
                    major_lesson.major_directions=data['major_directions']
                except:
                    pass
                major_lesson.if_degree=data['if_degree']
                try:
                    major_lesson.save()
                    desc = '{0}级{1}'.format(data['grade'], data['name'])
                    SpiderLogDetail.objects.create(spider_log_id=log_id, model='MajorLesson', status='success', desc=desc)
                    print(major_lesson,'创建成功')
                    return major_lesson
                except:
                    # print(str(data['major'].name) + str(data['major_directions']) + str(data['lesson_id']) + ' exist')
                    print('专业课程保存失败')
                    desc = '{0}级{1}'.format(data['grade'], data['name'])
                    SpiderLogDetail.objects.create(spider_log_id=log_id, model='Major', status='error', desc=desc)
                    return None
            else:
                print('专业课程已存在')
                desc = '{0}级{1}'.format(data['grade'], data['name'])
                SpiderLogDetail.objects.create(spider_log_id=log_id, model='Major', status='error', desc=desc)
                return major_lesson.first()
        else:
            major_lesson = MajorLesson.objects.filter(major=data['major'], lesson_id=data['lesson_id'])
            if not major_lesson:
                major_less = MajorLesson()
                try:
                    lesson = Lesson.objects.get(id=data['lesson_id'])
                except:
                    lesson = Lesson(id=data['lesson_id'], name=data['lesson_name'], credit=data['lesson_credit'])
                    lesson.save()
                    # lesson=self.create_lesson_object(lesson_id=data['lesson_id'])
                major_less.major=data['major']
                major_less.lesson = lesson
                major_less.lesson_type = data['lesson_type']
                major_less.open_semester = data['open_semester']
                try:
                    major_less.limit_lesson_minimum_credit = data['limit_lesson_minimum_credit']
                except:
                    pass
                major_less.if_degree = data['if_degree']
                try:
                    major_less.save()
                    desc = '{0}级{1}'.format(data['grade'], data['name'])
                    SpiderLogDetail.objects.create(spider_log_id=log_id, model='Major', status='success', desc=desc)
                    print(major_less, '创建成功')
                    return major_less
                except:
                    # print(str(data['major'].name) + str(data['major_directions']) + str(data['lesson_id']) + ' exist')
                    print('专业课程保存失败')
                    desc = '{0}级{1}'.format(data['grade'], data['name'])
                    SpiderLogDetail.objects.create(spider_log_id=log_id, model='Major', status='error', desc=desc)
                    print(major_less)
                    return None
            else:
                print('专业课程已存在！')
                desc = '{0}级{1}'.format(data['grade'], data['name'])
                SpiderLogDetail.objects.create(spider_log_id=log_id, model='Major', status='error', desc=desc)
                return major_lesson.first()
            # major_lesson=MajorLesson.objects.filter(major=data['major'],lesson_id=data['lesson_id'],major__if_multiple_directions=True,major_directions=data['major_directions'])


    def get_student(self):
        classes=Class.objects.all()
        for cla in classes:
            self.get_one_class_students(colloge_post_code=cla.colloge.post_code,class_post_code=cla.post_code)

    def semester2grade(self,semester):
        spli=semester.split('/')
        month=spli[1]
        if month=='9':
            gra=spli[0][2:]
            grade=int(gra)
            # print(grade)
            return grade
        else:
            return ''



    def get_one_grade_one_major(self,log_id,grade,major,limit_time=5,timeout=3):
        try:
            mmmajor_id=major['post_code'].strip()
            grrade=self.semester2grade(grade)
            mmmajor=Major.objects.filter(grade=grrade,major_id=mmmajor_id)
            if mmmajor:
                return None
            else:
                url = r'http://jwc.jxnu.edu.cn/User/default.aspx?&code=104&&uctl=MyControl\all_jxjh.ascx'
                hid = self.__get_hid_data(url=url)
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
                web_data = self.__s.post(url=url, data=form_data, timeout=timeout)
                web_data = web_data.text.replace('<br />', '').replace('<br>', '').replace('<br/>', '')
                soup = BeautifulSoup(web_data, 'html5lib')
                try:
                    lis = soup.select('table[width="98%"] > tbody > tr:nth-of-type(6) > td > li')
                    try:
                        trs = soup.select(
                            'table[width="98%"] > tbody > tr:nth-of-type(2) > td > table > tbody > tr:nth-of-type(3) > td > table > tbody > tr')
                        training_objectives = trs[0].select('td')[1].get_text().strip()
                        bs = trs[1].select('td:nth-of-type(2) > b')
                        # basic_knowledge = str(bs[0].nextSibling).strip().replace('\n', '').replace(' ', '').replace('\xa0','')
                        # major_knowledge = str(bs[1].nextSibling).strip().replace('\n', '').replace(' ', '').replace('\xa0','')
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
                        data = {
                            'major_id': major['post_code'].strip(),
                            'post_code': major['post_code'],
                            'grade': gra,
                            'name': major['major_name'].strip(),
                            'training_objectives': training_objectives,
                            # 'basic_knowledge':basic_knowledge,
                            # 'major_knowledge':major_knowledge,
                            'direction_introduction': major_direction_introduction,
                            'subject': major_type,
                            'main_subject': main_subject,
                            'similar_major': similar_major,
                            'education_background': education_background,
                            'degree': degree,
                            'length_of_schooling': length_of_schooling,
                            'minimum_graduation_credit': minimum_graduation_credit,
                            'if_multiple_directions': True if len(lis) > 1 else False,
                        }
                        print(data)
                        the_major = self.__MajorToObject(log_id=log_id,data=data)
                    except:
                        data = {
                            'major_id': major['post_code'].strip(),
                            'post_code': major['post_code'],
                            'grade': gra,
                            'name': major['major_name'].strip(),
                        }
                        try:
                            the_major = Major.objects.create(major_id=data['major_id'], post_code=data['post_code'],grade=data['grade'], name=data['name'])
                            desc = '{0}级{1}'.format(data['grade'], data['name'])
                            SpiderLogDetail.objects.create(spider_log_id=log_id, model='Major', status='success',desc=desc)
                        except:
                            the_major = Major.objects.get(major_id=data['major_id'], grade=data['grade'])
                            desc = '{0}级{1}'.format(data['grade'], data['name'])
                            SpiderLogDetail.objects.create(spider_log_id=log_id, model='Major', status='fail',desc=desc)
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
                                lesson_name = tds[2].get_text().strip(),
                                lesson_type = tds[0].get_text().strip()
                                try:
                                    open_semester=int(tds[-1].get_text().strip().replace('第','').replace('学期',''))
                                except:
                                    open_semester=1
                                if lesson_type == '公共必修':
                                    lesson_type = 1
                                elif lesson_type == '学科基础':
                                    lesson_type = 2
                                elif lesson_type == '专业主干':
                                    lesson_type = 3
                                else:
                                    lesson_type = 4
                                data = {
                                    'major': the_major,
                                    'lesson_id': tds[1].get_text().strip(),
                                    'lesson_type': lesson_type,
                                    'if_degree': True if tds[3].get_text().strip() == '是' else False,
                                    'lesson_name': lesson_name,
                                    'lesson_credit': lesson_credit,
                                    'open_semester':open_semester,
                                }
                                print(data)
                                self.__MajorLessonToObject(log_id,data)
                    except:
                        pass

                    try:
                        tables=soup.select('table[width="98%"] > tbody > tr:nth-of-type(6) > td > table')
                        tbodys = soup.select('table[width="98%"] > tbody > tr:nth-of-type(6) > td > table > tbody')
                        # lisss = []
                        for tbody, li,table in zip(tbodys,lis,tables):
                            try:
                                limit_lesson_minimum_credit=int(table.previous_sibling.strip().replace('在下列课程中至少应选修','').replace('学分','').strip())
                            except:
                                print('获取学分异常，采用默认38分')
                                limit_lesson_minimum_credit=38
                            trs = tbody.select('tr')
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
                                try:
                                    open_semester=int(tds[-1].get_text().strip().replace('第','').replace('学期',''))
                                except:
                                    open_semester=1
                                if the_major.if_multiple_directions == True:
                                    data = {
                                        'major': the_major,
                                        'lesson_id': tds[1].get_text().strip(),
                                        'lesson_type': 5,
                                        'if_degree': False,
                                        'major_directions': uck_major_direction,
                                        'lesson_credit': lesson_credit,
                                        'lesson_name': tds[2].get_text().strip(),
                                        'open_semester': open_semester,
                                        'limit_lesson_minimum_credit':limit_lesson_minimum_credit,
                                    }
                                    print(data)
                                    self.__MajorLessonToObject(log_id=log_id,data=data)
                                else:
                                    data = {
                                        'major': the_major,
                                        'lesson_id': tds[1].get_text().strip(),
                                        'lesson_type': 5,
                                        'if_degree': False,
                                        'lesson_credit': lesson_credit,
                                        'lesson_name': tds[2].get_text().strip(),
                                        'open_semester': open_semester,
                                        'limit_lesson_minimum_credit':limit_lesson_minimum_credit,
                                    }
                                    print(data)
                                    self.__MajorLessonToObject(log_id,data)
                    except:
                        pass
                except:
                    pass
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_one_grade_one_major timeout, retrying。。')
                return self.get_one_grade_one_major(log_id=log_id,grade=grade,major=major,limit_time=limit_ti)
            else:
                return None




    def update_one_grade_one_major(self,grade,major,major_obj,limit_time=5,timeout=3):
        try:
            # mmmajor_id=major['post_code'].strip()
            # grrade=self.semester2grade(grade)
            # mmmajor=Major.objects.filter(grade=grrade,major_id=mmmajor_id)
            # if not mmmajor:
            #     return None
            # else:
            url = r'http://jwc.jxnu.edu.cn/User/default.aspx?&code=104&&uctl=MyControl\all_jxjh.ascx'
            hid = self.__get_hid_data(url=url)
            # gra = int(grade.split('/')[0][2:])
            form_data = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': hid[0],
                '__EVENTVALIDATION': hid[1],
                '_ctl1:Nianji': grade,
                '_ctl1:zhuanye': major['post_code'],
                '_ctl1:GoSearch': '查询'
            }
            web_data = self.__s.post(url=url, data=form_data, timeout=timeout)
            web_data = web_data.text.replace('<br />', '').replace('<br>', '').replace('<br/>', '')
            soup = BeautifulSoup(web_data, 'html5lib')
            try:
                lis = soup.select('table[width="98%"] > tbody > tr:nth-of-type(6) > td > li')
                # try:
                #     trs = soup.select(
                #         'table[width="98%"] > tbody > tr:nth-of-type(2) > td > table > tbody > tr:nth-of-type(3) > td > table > tbody > tr')
                #     training_objectives = trs[0].select('td')[1].get_text().strip()
                #     bs = trs[1].select('td:nth-of-type(2) > b')
                #     # basic_knowledge = str(bs[0].nextSibling).strip().replace('\n', '').replace(' ', '').replace('\xa0','')
                #     # major_knowledge = str(bs[1].nextSibling).strip().replace('\n', '').replace(' ', '').replace('\xa0','')
                #     major_direction_introduction = trs[2].select('td')[1].get_text().strip()
                #     major_type = trs[3].select('td')[1].get_text().strip()
                #     main_subject = trs[4].select('td')[1].get_text().strip()
                #     similar_major = trs[5].select('td')[1].get_text().strip()
                #     tds = trs[6].select('td')
                #     education_background = tds[1].get_text().strip()
                #     try:
                #         length_of_schooling = int(tds[3].get_text().strip().strip('年').strip())
                #     except:
                #         length_of_schooling = 4
                #     degree = tds[5].get_text().strip()
                #     try:
                #         minimum_graduation_credit = int(tds[7].get_text().strip())
                #     except:
                #         minimum_graduation_credit = 160
                #     # major_data = {
                #     #     'uck_grade': gra,
                #     #     'major_id': major['major_id'],
                #     #     'uck_major_name': major['major_name'],
                #     #     'training_objectives': None if training_objectives == '' else training_objectives,
                #     #     'basic_knowledge': None if basic_knowledge[1:-2] == ['', '', ''] else basic_knowledge[1:-2],
                #     #     'major_knowledge': None if major_knowledge[1:-2] == ['', ''] else major_knowledge[1:-2],
                #     #     'major_direction_introduction': major_direction_introduction,
                #     #     'major_type': major_type,
                #     #     'main_subject': main_subject,
                #     #     'similar_major': similar_major,
                #     #     'education_background': education_background,
                #     #     'length_of_schooling': length_of_schooling,
                #     #     'degree': degree,
                #     #     'minimum_graduation_credit': minimum_graduation_credit,
                #     # }

                #     data = {
                #         'major_id': major['post_code'].strip(),
                #         'post_code': major['post_code'],
                #         'grade': gra,
                #         'name': major['major_name'].strip(),
                #         'training_objectives': training_objectives,
                #         # 'basic_knowledge':basic_knowledge,
                #         # 'major_knowledge':major_knowledge,
                #         'direction_introduction': major_direction_introduction,
                #         'subject': major_type,
                #         'main_subject': main_subject,
                #         'similar_major': similar_major,
                #         'education_background': education_background,
                #         'degree': degree,
                #         'length_of_schooling': length_of_schooling,
                #         'minimum_graduation_credit': minimum_graduation_credit,
                #         'if_multiple_directions': True if len(lis) > 1 else False,
                #     }
                #     # print(data)
                #     the_major = self.__MajorToObject(data)
                # except:
                #     data = {
                #         'major_id': major['post_code'].strip(),
                #         'post_code': major['post_code'],
                #         'grade': gra,
                #         'name': major['major_name'].strip(),
                #     }
                #     try:
                #         the_major = Major.objects.create(major_id=data['major_id'], post_code=data['post_code'],
                #                                          grade=data['grade'], name=data['name'])
                #     except:
                #         the_major = Major.objects.get(major_id=data['major_id'], grade=data['grade'])
                the_major=major_obj
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
                            lesson_name = tds[2].get_text().strip(),
                            lesson_type = tds[0].get_text().strip()
                            try:
                                semee=tds[-1].get_text().strip()
                                open_semester=int(semee.replace('第','').replace('学期',''))
                            except:
                                open_semester=1
                            if lesson_type == '公共必修':
                                lesson_type = 1
                            elif lesson_type == '学科基础':
                                lesson_type = 2
                            elif lesson_type == '专业主干':
                                lesson_type = 3
                            else:
                                lesson_type = 4
                            data = {
                                'major': the_major,
                                'lesson_id': tds[1].get_text().strip(),
                                'lesson_type': lesson_type,
                                'if_degree': True if tds[3].get_text().strip() == '是' else False,
                                'lesson_name': lesson_name,
                                'lesson_credit': lesson_credit,
                                'open_semester':open_semester,
                            }
                            # print(data)
                            major_lesson=MajorLesson.objects.filter(major=the_major,lesson_id=data['lesson_id'])
                            if major_lesson:
                                major_lesson[0].open_semester=data['open_semester']
                                major_lesson[0].save()
                                # print(major_lesson[0])
                            else:
                                print('专业课未找到，正在创建...')
                                major_lesso=self.__MajorLessonToObject(data)
                                if major_lesso:
                                    print('创建成功')
                                else:
                                    print('创建失败')

                except:
                    pass

                try:
                    tables = soup.select('table[width="98%"] > tbody > tr:nth-of-type(6) > td > table')
                    tbodys = soup.select('table[width="98%"] > tbody > tr:nth-of-type(6) > td > table > tbody')
                    # lisss = []
                    for tbody, li, table in zip(tbodys, lis, tables):
                        try:
                            limit_lesson_minimum_credit = int(li.next_sibling.strip().replace('在下列课程中至少应选修', '').replace('学分', '').strip())
                            print('学分获取成功')
                        except:
                            print('获取学分异常，采用默认38分, 内容：',li.next_sibling)
                            limit_lesson_minimum_credit = 38
                        trs = tbody.select('tr')
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
                            try:
                                open_semester=int(tds[-1].get_text().strip().replace('第','').replace('学期',''))
                            except:
                                open_semester=1
                            if the_major.if_multiple_directions == True:
                                data = {
                                    'major': the_major,
                                    'lesson_id': tds[1].get_text().strip(),
                                    'lesson_type': 5,
                                    'if_degree': False,
                                    'major_directions': uck_major_direction,
                                    'lesson_credit': lesson_credit,
                                    'lesson_name': tds[2].get_text().strip(),
                                    'open_semester': open_semester,
                                    'limit_lesson_minimum_credit':limit_lesson_minimum_credit,
                                }
                                # print(data)
                                major_lesson = MajorLesson.objects.filter(major=the_major,lesson_id=data['lesson_id'],major_directions=data['major_directions'])
                                if major_lesson:
                                    major_lesson[0].limit_lesson_minimum_credit = data['limit_lesson_minimum_credit']
                                    major_lesson[0].save()
                                    # print(major_lesson[0])
                                else:
                                    print('未找到多方向专业限选课程,正在创建...')
                                    major_lesso = self.__MajorLessonToObject(data)
                                    if major_lesso:
                                        print('创建成功')
                                    else:
                                        print('创建失败')
                                # self.__MajorLessonToObject(data)
                            else:
                                data = {
                                    'major': the_major,
                                    'lesson_id': tds[1].get_text().strip(),
                                    'lesson_type': 5,
                                    'if_degree': False,
                                    'lesson_credit': lesson_credit,
                                    'lesson_name': tds[2].get_text().strip(),
                                    'open_semester': open_semester,
                                    'limit_lesson_minimum_credit':limit_lesson_minimum_credit,
                                }
                                major_lesson = MajorLesson.objects.filter(major=the_major,lesson_id=data['lesson_id'])
                                if major_lesson:
                                    major_lesson[0].limit_lesson_minimum_credit = data['limit_lesson_minimum_credit']
                                    major_lesson[0].save()
                                    # print(major_lesson[0])
                                else:
                                    print('未找到单方向专业限选课程，正在创建...')
                                    major_lesso = self.__MajorLessonToObject(data)
                                    if major_lesso:
                                        print('创建成功')
                                    else:
                                        print('创建失败')
                                # print(data)
                                # self.__MajorLessonToObject(data)
                except:
                    pass
            except:
                pass
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('update_one_grade_one_major timeout, retrying。。')
                return self.update_one_grade_one_major(grade=grade,major=major,major_obj=major_obj,limit_time=limit_ti)
            else:
                return None

    def update_all_majorlesson(self):
        majors=Major.objects.all()
        for maj in majors:
            major={'post_code':maj.post_code,'major_name':maj.name}
            grade_list = self.grade_list
            # print(major_id)
            for grade in grade_list:
                # print(grade)
                self.update_one_grade_one_major(grade=grade['post_code'], major=major,major_obj=maj)




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
            grade_list = self.grade_list
            # print(major_id)
            for grade in grade_list:
                # print(grade)
                self.get_one_grade_one_major(grade=grade['post_code'],major=major)

    def get_one_grade_major(self,log_id,grade_post_code):
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
            major = {
                'post_code': post_code,
                'major_name': maj,
            }
            # grade_list = self.grade_list
            # print(major_id)
            # for grade in grade_list:
                # print(grade)
            self.get_one_grade_one_major(log_id=log_id,grade=grade_post_code, major=major)


    def get_student_photo(self,user,timeout=4,limit_time=5):
        try:
            if not user.image:
                url=r'http://jwc.jxnu.edu.cn/StudentPhoto/{}.jpg'.format(user.username)
                img_data = self.__s.get(url,timeout=timeout)
                if img_data.status_code==requests.codes.ok:
                    with open('../media/imgs/student/'+user.username+'.jpg','wb') as photo:
                        photo.write(img_data.content)
                        photo.close()
                    img='imgs/student/'+user.username+'.jpg'
                    user.image=img
                    user.save()
                    return
                else:
                    print('获取头像异常，url: ',url)
                    return
            else:
                print('头像已存在')
                return
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_teachget_student_photoer_photo timeout, retrying。。')
                return self.get_student_photo(user=user, limit_time=limit_ti)
            else:
                return None






if __name__ == '__main__':
    spd=SpiderStaticStudent(MY_USERNAME,MY_WORD)
    spd.sign_in()
    # spd.get_class(colloge_post_code='57000   ')
    # for i in range(200):
    #     spd.sign_in()
    # print(MY_WORD,MY_USERNAME)
    # spd.sign_in(limit_time=20)
    # spd.update_all_majorlesson()
    # spd.get_colloges()
    # spd.get_class()
    # spd.get_one_colloge_classes(colloge_code='57000   ')
    # spd.get_one_class_students(colloge_post_code='49000   ',class_post_code='24982425A           ')
    # spd.get_student()
    # spd.get_one_grade_one_major('2018/9/1 0:00:00',{'post_code':'130101W ','major_name':'表演（戏剧影视）'})
    # spd.get_major()
    # for i in spd.grade_list:
    #     print(i['post_code'])
    # spd.get_one_grade_one_major('2018/9/1 0:00:00',{'post_code':'050204  ','major_name':'法语'})
    # spd.get_major()
    # spd.semester2grade('2019/9/1 0:00:00')





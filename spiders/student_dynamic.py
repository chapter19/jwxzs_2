#-*- coding:utf-8 -*-

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
django.setup()

from jwxzs_2.settings import VERIFICATIONCODE_SRC

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

class SpiderDynamicStudent:
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
    def sign_in(self,limit_time=10,timeout=4):
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
                print(self.id)
                print(self.password)
                return None

    def test(self):
        url='http://jwc.jxnu.edu.cn/Portal/Index.aspx'
        wb_data=requests.get(url)
        print(wb_data.text)

    def __create_class_id(self):
        auth = ""  # 定义全局验证码变量
        for i in range(0, 9):  # 定义循环4次，形成4位验证码。
            # current = random.randint(0, 4)  # 定义一个随机0-4的一个范围，去猜i 的值。
            # if current == i:  # 如果current 和i 的值一样
            #     current_code = random.randint(0, 9)  # 生成一个随机的数字
            # else:  # 如果current和i 的值不一样
            current_code = chr(random.randint(65, 90))  # 生成一个随机的字母，这里一定要主义chr（）转换一下。
            auth += str(current_code)  # 将每次随机生成的值赋值给auth
        return '|'+auth

    def __update_score(self,data):
        try:
            score=Score.objects.get(student=data['student'],schedule_lesson__semester=data['semester'],schedule_lesson__lesson_id=data['lesson_id'])
            score.score=data['score']
            score.standard_score=data['standard_score']
            score.if_major=data['if_major']
            score.rescore=data['rescore']
            score.save()
        except:
            score=Score()
            score.student=data['student']
            schedule_lesson=ScheduleLesson.objects.filter(lesson_id=data['lesson_id'],class_name__startswith='|',semester=data['semester'])
            if schedule_lesson:
                schedule_lesson=schedule_lesson[0]
            else:
                schedule_lesson=ScheduleLesson()
                class_id=self.__create_class_id()
                schedule_lesson.class_id=class_id
                schedule_lesson.class_name=class_id
                schedule_lesson.semester=data['semester']
                schedule_lesson.lesson_id=data['lesson_id']
                schedule_lesson.save()
            score.schedule_lesson=schedule_lesson
            score.score = data['score']
            score.standard_score = data['standard_score']
            score.if_major = data['if_major']
            score.rescore = data['rescore']
            score.save()



    # 获取成绩单
    def get_my_studyData(self,error_time_limit=10,timeout=4):
        try:
            student = Student.objects.get(id=self.id)
            mmajor = student.cla.major

            stud=self.id
            s=0
            semsters=[{'num':0,'semester':''}]
            lessons=[]
            url=r'http://jwc.jxnu.edu.cn/MyControl/All_Display.aspx?UserControl=xfz_cj.ascx&Action=Personal'
            wb_data=self.__s.get(url,timeout=timeout)
            soup=BeautifulSoup(wb_data.text,"html5lib")
            # print(soup)
            my_credit=soup.select('#_ctl11_lblMsg > u')[5]
            nu=soup.select('td[valign="middle"]')
            for n in nu:
                dat={
                    'num':int(n.get('rowspan')),
                    'semester':n.select('font')[0].get_text()
                }
                # print(dat)
                semsters.append(dat)
            # print(semsters)
            lessons = soup.select('tr[bgcolor="White"]')
            # print(lessons)
            for i in range(1,len(semsters)):
                # print(semsters[i]['num'])
                l=''
                locals()['semster'+str(i)]=lessons[s:s+semsters[i]['num']]
                for ss in range(0,len(locals()['semster'+str(i)])):
                    if ss==0:
                        semster = locals()['semster' + str(i)][ss].select('td[valign="middle"] > font')[0].get_text().strip().split('-')
                        bbbb=semster[1].split('第')
                        aaaa=bbbb[1][:1]
                        semester=''
                        if aaaa=='1':
                            semester='20{0}/9/1 0:00:00'.format(semster[0])
                        elif aaaa=='2':
                            semester='20{0}/3/1 0:00:00'.format(bbbb[0])
                        else:
                            pass
                        d=locals()['semster'+str(i)][ss].select('td > font')
                        # print(d)
                        cre=d[3].get_text().strip()
                        sco=d[4].get_text().strip()
                        sta=d[6].get_text().strip()
                        ret=d[5].get_text().strip()
                        if cre=='':
                            cre=0
                        if sco=='':
                            sco=0
                        if sta=='':
                            sta=-20
                        try:
                            ret=float(ret)
                        except:
                            if float(sco)>=60:
                                ret=None
                            else:
                                ret=0.0
                        uck_lesson_id1 = d[1].get_text().strip()

                        try:
                            aaa=MajorLesson.objects.get(major=mmajor,lesson_id=uck_lesson_id1)
                            is_major_lesson = False
                            if aaa.lesson_type in [3,4,5]:
                                is_major_lesson=True
                            elif aaa.lesson_type==2:
                                naaaa = aaa.lesson.name
                                if '公共必修' or '高等数学' not in naaaa:
                                    is_major_lesson = True
                            else:
                                pass

                            data={
                                'student':student,
                                'lesson_id':uck_lesson_id1,
                                'semester':semester,
                                'score':float(sco),
                                'rescore':ret,
                                'standard_score':float(sta),
                                'if_major':is_major_lesson
                            }
                            print(data)
                            self.__update_score(data)
                        except:
                            data = {
                                'student': student,
                                'lesson_id': uck_lesson_id1,
                                'semester': semester,
                                'score': float(sco),
                                'rescore': ret,
                                'standard_score': float(sta),
                                'if_major': False,
                            }
                            print(data)
                            self.__update_score(data)
                        l = semester
                    else:
                        d = locals()['semster' + str(i)][ss].select('td > font')
                        cre=d[2].get_text().strip()
                        sco=d[3].get_text().strip()
                        sta=d[5].get_text().strip()
                        ret=d[4].get_text().strip()
                        if cre=='':
                            cre=0
                        if sco=='':
                            sco=0
                        if sta=='':
                            sta=-20
                        try:
                            ret=float(ret)
                        except:
                            if float(sco)>=60:
                                ret=None
                            else:
                                ret=0.0
                        uck_lesson_id=d[0].get_text().strip()
                        if uck_lesson_id!='':
                            pass
                        else:
                            uck_lesson_id=None
                        try:
                            aaa=MajorLesson.objects.get(major=mmajor,lesson_id=uck_lesson_id)
                            is_major_lesson = False
                            if aaa.lesson_type in [3,4,5]:
                                is_major_lesson=True
                            elif aaa.lesson_type==2:
                                naaaa=aaa.lesson.name
                                if '公共必修' or '高等数学' not in naaaa:
                                    is_major_lesson = True
                            else:
                                pass
                            data={
                                'student':student,
                                'lesson_id':uck_lesson_id,
                                'semester':l,
                                'score':float(sco),
                                'rescore':ret,
                                'standard_score':float(sta),
                                'if_major':is_major_lesson
                            }
                            print(data)
                            self.__update_score(data)
                        except:
                            data = {
                                'student': student,
                                'lesson_id': uck_lesson_id,
                                'semester': l,
                                'score': float(sco),
                                'rescore': ret,
                                'standard_score': float(sta),
                                'if_major': False
                            }
                            print(data)
                            self.__update_score(data)
                s += semsters[i]['num']
            # print(lessons)
        except:
            error_time_limit -= 1
            if error_time_limit > 0:
                print('get_my_studyPlan timeout, retrying。。')
                return self.get_my_studyData(error_time_limit=error_time_limit)
            else:
                return 0

    def __TotalCreditToObject(self,data):
        total_credit=TotalCredit()
        try:
            student=Student.objects.get(id=data['student_id'])
            total_credit.student=student
            total_credit.credit=data['credit']
            total_credit.standard_score=data['standard_score']
            total_credit.save()
        except:
            print(data['student_id']+' total_credit插入失败')


    #获取个人学习预警已修课程情况
    def get_my_studyPlan(self,error_time_limit=10,timeout=4):
        try:
            url='http://jwc.jxnu.edu.cn/MyControl/All_Display.aspx?UserControl=xfz_bysh.ascx&Action=Personal'
            wb_data=self.__s.get(url,timeout=timeout)
            soup=BeautifulSoup(wb_data.text,'html5lib')
            # print(soup)
            thestudata=soup.select('#_ctl11_lblInfor > br')
            # buttons=soup.select('#_ctl11_lblInfor > div.button')
            list=thestudata[0].previous_sibling.split()
            studentdate=soup.select('#_ctl11_lblTitle > u')
            try:
                major=studentdate[0].get_text().strip()
            except:
                major=None

            try:
                student=Student.objects.get(id=self.id)
                if student.cla.major:
                    pass
                else:
                    cla=student.cla
                    try:
                        majo=Major.objects.filter(name=major,grade=cla.grade)
                        cla.major=majo[0]
                        cla.save()
                    except:
                        pass
            except:
                pass
            try:
                theAllCredit=int(list[1].split('：')[1])
            except:
                theAllCredit=0
            try:
                theAllStandardSCORE = float(list[2].split('：')[1])
            except:
                theAllStandardSCORE = None
            data={
                'student_id':self.id,
                'credit':theAllCredit,
                'standard_score':theAllStandardSCORE,
            }
            print(data)
            self.__TotalCreditToObject(data=data)
        except:
            error_time_limit -= 1
            if error_time_limit > 0:
                print('get_my_studyPlan timeout, retrying。。')
                return self.get_my_studyPlan(error_time_limit=error_time_limit)
            else:
                return 0

    def __StudentDetailToObject(self,data):
        student_detail=StudentDetail()
        try:
            student=Student.objects.get(id=data['student_id'])
            student_detail.base_data=student
        except:
            student=None
            print('student get error')

        student_detail.candidate_id=data['candidate_id']
        student_detail.nationality=data['nationality']
        student_detail.birthday=data['birthday']
        student_detail.id_card=data['id_card']
        student_detail.political_status=data['political_status']
        student_detail.birthplace=data['birthplace']
        student_detail.email=data['email']
        student_detail.mobile=data['mobile']
        try:
            user_profile=UserProfile.objects.get(username=data['student_id'])
            user_profile.name=student.name
            user_profile.gender=student.gender
            user_profile.save()
            student_detail.user_profile=user_profile
        except:
            print('user profile get error')
        # student_detail.user_profile_username=data['student_id']
        try:
            student_detail.save()
        except:
            print('StudentDetail insert error')

    #获取个人信息
    def get_student_detail_data(self,error_time_limit=10,timeout=4):
        try:
            url1='http://jwc.jxnu.edu.cn/MyControl/Student_InforCheck.aspx'
            url2='http://jwc.jxnu.edu.cn/MyControl/All_Display.aspx?UserControl=All_StudentInfor.ascx&UserType=Student&UserNum='+self.id
            # code=''
            # code2=''
            # error_time1=0
            wb_data1=self.__s.get(url1,timeout=timeout)
            soup1=BeautifulSoup(wb_data1.text,'html5lib')
            try:
                student_examinee_id=soup1.select('#lblKSH')[0].get_text().strip()
                if student_examinee_id!='':
                    pass
                else:
                    student_examinee_id=None
            except:
                student_examinee_id = None
            try:
                student_nationality=soup1.select('#lblMZ')[0].get_text().strip()
                if student_nationality!='':
                    pass
                else:
                    student_nationality=None
            except:
                student_nationality=None
            try:
                student_id_card_id=soup1.select('#lblSFZH')[0].get_text().strip()
                if student_id_card_id!='':
                    pass
                else:
                    student_id_card_id=None
            except:
                student_id_card_id=None
            wb_data2 = self.__s.get(url2)
            # print(wb_data2)
            soup2=BeautifulSoup(wb_data2.text,'html5lib')
            # print(soup2)
            try:
                student_political_status= soup2.select('#_ctl11_lblZZMM')[0].get_text().strip()
                if student_political_status!='':
                    pass
                else:
                    student_political_status=None
            except:
                student_political_status=None
            try:
                student_birthplace=soup2.select('#_ctl11_lblJG')[0].get_text().strip()
                if student_birthplace!='':
                    pass
                else:
                    student_birthplace=None
            except:
                student_birthplace=None
            try:
                student_email=soup2.select('#_ctl11_lblYJ')[0].get_text().strip()
                if student_email!='':
                    pass
                else:
                    student_email=None
            except:
                student_email=None
            try:
                student_telephone_number=soup2.select('#_ctl11_lblTXHM')[0].get_text().strip()
                if student_telephone_number!='':
                    pass
                else:
                    student_telephone_number=None
            except:
                student_telephone_number=None
            try:
                birthday=soup2.select('#_ctl11_lblCSRQ')[0].get_text().strip()
                bir_split1=birthday.split('年')
                try:
                    student_birth_year=int(bir_split1[0].strip())
                except:
                    student_birth_year=1940
                bir_split2=bir_split1[1].split('月')
                try:
                    student_birth_month=int(bir_split2[0].strip())
                except:
                    student_birth_month=1
                try:
                    student_birth_day=int(bir_split2[1].strip('日').strip())
                except:
                    student_birth_day=1
            except:
                student_birth_year=None
                student_birth_month=None
                student_birth_day=None
            data={
                'student_id':self.id,
                'candidate_id':student_examinee_id,
                'nationality':student_nationality,
                'birthday':'{0}-{1}-{2}'.format(student_birth_year,student_birth_month,student_birth_day),
                'id_card':student_id_card_id,
                'political_status':student_political_status,
                'birthplace':student_birthplace,
                'email':student_email,
                'mobile':student_telephone_number,
            }
            print(data)
            self.__StudentDetailToObject(data=data)
        except:
            error_time_limit -= 1
            if error_time_limit > 0:
                print('get_student_detail_data timeout, retrying。。')
                return self.get_student_detail_data(error_time_limit=error_time_limit)
            else:
                return None

    def get_all_data(self):
        self.get_my_studyPlan()
        self.get_my_studyData()
        self.get_student_detail_data()

if __name__ == '__main__':
    me=SpiderDynamicStudent('201626703079','m19980220')
    # me=SpiderDynamicStudent('1467005018','687196')
    me.sign_in()
    # me.get_my_studyData()
    # me.get_all_data()
    # me.test()
    # a=me.create_class_id()
    # print(a)






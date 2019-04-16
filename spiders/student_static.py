#-*- coding:utf-8 -*-

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
django.setup()

from jwxzs_2.settings import VERIFICATIONCODE_SRC\
    # ,GRADE_LIST

import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import uuid,os,time
from users.models import Colloge,Class,Student,Major
from lessons.models import MajorLesson,Lesson
from semesters.models import Semester


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
            soup = BeautifulSoup(web_data, 'html5lib')
            try:
                trs = soup.select('table[width="98%"] > tbody > tr:nth-of-type(2) > td > table > tbody > tr:nth-of-type(3) > td > table > tbody > tr')
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
            grade_list = self.grade_list
            # print(major_id)
            for grade in grade_list:
                self.get_one_grade_one_major(grade=grade['post_code'],major=major)


if __name__ == '__main__':
    spd=SpiderStaticStudent('201626703079','m19980220')
    spd.sign_in(limit_time=20)
    # spd.get_colloges()
    # spd.get_class()
    # spd.get_one_colloge_classes(colloge_code='57000   ')
    # spd.get_one_class_students(colloge_post_code='49000   ',class_post_code='24982425A           ')
    # spd.get_student()
    # spd.get_one_grade_one_major('2018/9/1 0:00:00',{'post_code':'130101W ','major_name':'表演（戏剧影视）'})
    # spd.get_major()
    # for i in spd.grade_list:
    #     print(i['post_code'])







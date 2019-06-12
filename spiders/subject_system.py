#-*- coding:utf-8 -*-

import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")  # project_name 项目名称
django.setup()

import requests
from bs4 import BeautifulSoup
import jieba
# import pymongo

from subject.models import LessonLabels
from users.models import Teacher
from semesters.models import Semester,NextSemester,CurrentSemester
from subject.models import StepOneLessonTeacher,MyXuanKe
from lessons.models import Lesson

from utils.settings import MY_USERNAME,MY_WORD

class Pingjiao:
    def __init__(self,student_id=MY_USERNAME,student_password=MY_WORD):
        # self.__client=pymongo.MongoClient(host="localhost",port=27017,connect=False)
        # self.__sebject_system=self.__client['xzs_spider_subject_system']
        # self.__sebject_system.authenticate(name='xzs_spider_subject_system_user',password='xsssum2567076458')
        # self.__sebject_system_lesson = self.__sebject_system['sebject_system_lesson']
        # self.__sebject_system_lesson.create_index([('uk_lesson_id', 1)], unique=True)

        self.student_id=student_id
        self.student_password=student_password
        self.__session=requests.Session()
        self.next_semester = NextSemester.objects.first().next_semester

    # 取出表单隐藏值的私有方法
    def __get_hid_data(self, url):
        # 先get请求一次
        wb_data = self.__session.get(url)
        soup = BeautifulSoup(wb_data.text, 'lxml')
        # 从get请求后反馈的response中找出两个隐藏值
        __VIEWSTATE = soup.select("input[name='__VIEWSTATE']")[0].get('value')
        __VIEWSTATEGENERATOR = soup.select("input[name='__VIEWSTATEGENERATOR']")[0].get('value')
        __EVENTVALIDATION = soup.select("input[name='__EVENTVALIDATION']")[0].get('value')
        # 返回两个隐藏值
        return __VIEWSTATE,__VIEWSTATEGENERATOR,__EVENTVALIDATION

    def login(self):
        url='http://xk.jxnu.edu.cn/default.aspx'
        hid_data=self.__get_hid_data(url)
        post_data={
            '__VIEWSTATE':hid_data[0],
            '__VIEWSTATEGENERATOR':hid_data[1],
            '__EVENTVALIDATION':hid_data[2],
            'txtUserNum':self.student_id,
            'txtPassword':self.student_password,
            'btnLogin':'登录'
        }
        wb_data=self.__session.post(url=url,data=post_data)
        soup=BeautifulSoup(wb_data.text,'html5lib')
        name=soup.select('#ctl00_lbtExit')[0].previousSibling.split('｜')[1].strip()
        print(name+' 登录成功\n')
        # print(wb_data.text)


    def get_my_pingjiao(self,timeout=2,limit_time=3,step='1'):
        try:
            url='http://xk.jxnu.edu.cn/Step%s/MyPJ_Detail.aspx'%step
            wb_data=self.__session.get(url,timeout=timeout)
            soup=BeautifulSoup(wb_data.text,'html5lib')
            trs=soup.select('#ctl00_chdContent_PjDetail1_gvContent > tbody > tr')
            li=[]
            for tr in trs[1:]:
                tds=tr.select('td')
                lesson_name=tds[1].get_text().strip()
                teacher_name=tds[2].get_text().strip()
                pj_code=tds[4].select('span.mypj')[0].get('id').split('-')[-1]
                teacher_id=tds[3].select('img')[0].get('src').split('?')[1].split('=')[1].split('&')[0]
                data={
                    'lesson_name':lesson_name,
                    # 'teacher_name':teacher_name,
                    'code':pj_code,
                    # 'teacher_id':teacher_id,
                    'teacher':{'name':teacher_name,'id':teacher_id}
                }
                li.append(data)
            print(li)
            return li
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_my_pingjiao timeout, retrying。。')
                return self.get_my_pingjiao(limit_time=limit_ti)
            else:
                return None


    def pingjiao(self,groupA='',groupB='',groupC='',groupD=''):
        # url='http://xk.jxnu.edu.cn/Step1/MyPj_detail.aspx?step=4'
        url='http://xk.jxnu.edu.cn/Step1/MyPJ_Detail.aspx'
        hid_data=self.__get_hid_data(url)
        for i in range(1,6):
            urll=url+'?step='+str(i)
            post_data={
                '__EVENTTARGET':'',
                '__EVENTARGUMENT':'',
                '__VIEWSTATE':hid_data[0],
                '__VIEWSTATEGENERATOR':hid_data[1],
                '__EVENTVALIDATION':hid_data[2],
                'groupA':groupA,
                'groupB':groupB,
                'groupC':groupC,
                'groupD':groupD,
                'ctl00$chdContent$PjDetail1$btnSave':'提交当前，进入下一步……' if i!=5 else '提交当前，完成本次评价……'
            }
            wb_data=self.__session.post(url=urll,data=post_data)
            soup=BeautifulSoup(wb_data.text,'html5lib')
            __VIEWSTATE = soup.select("input[name='__VIEWSTATE']")[0].get('value')
            __VIEWSTATEGENERATOR = soup.select("input[name='__VIEWSTATEGENERATOR']")[0].get('value')
            __EVENTVALIDATION = soup.select("input[name='__EVENTVALIDATION']")[0].get('value')
            hid_data=(__VIEWSTATE,__VIEWSTATEGENERATOR,__EVENTVALIDATION)
        print('评教成功，评教结果如下：\n')
        url2='http://xk.jxnu.edu.cn/Step1/MyPj.aspx'
        wb_data=self.__session.get(url2)
        soup=BeautifulSoup(wb_data.text,'html5lib')
        trs=soup.select('#ctl00_chdContent_PjIndex1_gvContent > tbody > tr[align="center"]')
        li=[]
        for tr in trs:
            tds=tr.select('td')
            # list=[tds[1].get_text().strip(),tds[2].get_text().strip(),tds[3].get_text().strip()]
            data={
                'lesson_name':tds[1].get_text().strip(),
                'teacher_name':tds[2].get_text().strip(),
                'grade':tds[3].get_text().strip(),
            }
            li.append(data)
        print(li)
        return li


    def __get_public_elective(self):
        url='http://xk.jxnu.edu.cn/Step1/AddCourseSearch.aspx'
        hid_data=self.__get_hid_data(url)
        __EVENTTARGET_list=['ctl00$chdContent$SearchCourse1$lbt02','ctl00$chdContent$SearchCourse1$lbt03','ctl00$chdContent$SearchCourse1$lbt04','ctl00$chdContent$SearchCourse1$lbt05']
        public_elective_lesson_type=['人文与社会','科学与技术','体育','艺术']
        for i,j in zip(__EVENTTARGET_list,public_elective_lesson_type):
            post_data={
                '__EVENTTARGET':i,
                '__EVENTARGUMENT':'',
                '__VIEWSTATE':hid_data[0],
                '__VIEWSTATEGENERATOR':hid_data[1],
                '__EVENTVALIDATION':hid_data[2],
                'ctl00$chdContent$SearchCourse1$ddlXkml':'0101    ',
                'ctl00$chdContent$SearchCourse1$ddlDW':'68000   ',
                'ctl00$chdContent$SearchCourse1$txtKey':''
            }
            wb_data=self.__session.post(url=url,data=post_data)
            # print(wb_data)
            soup=BeautifulSoup(wb_data.text,'html5lib')
            # print(soup)
            trs=soup.select('#ctl00_chdContent_SearchCourse1_gvContent > tbody > tr')
            # print(trs)
            for tr in trs[1:]:
                tds=tr.select('td')
                lesson_manage_unit=tds[1].get_text().strip()
                if lesson_manage_unit in ['','无']:
                    lesson_manage_unit=None
                else:
                    pass
                try:
                    lesson_open_turn=int(tds[6].get_text().strip().strip('每学年第学期').strip())
                except:
                    lesson_open_turn=None
                try:
                    lesson_credit=int(tds[4].get_text().strip())
                except:
                    lesson_credit=2
                before_learning=tds[5].get_text().strip()
                if before_learning not in ['','无','None']:
                    pass
                else:
                    before_learning=None
                try:
                    lesson_name=tds[3].get_text().strip()
                except:
                    lesson_name=None
                if lesson_name != None:
                    tags=self.__fenci(lesson_name)
                    if lesson_manage_unit != None:
                        tags.append(lesson_manage_unit)
                        tags.append(j)
                        tags=set(tags)
                        tags=list(tags)
                else:
                    if lesson_manage_unit != None:
                        tags=[lesson_manage_unit,j]
                    else:
                        tags=[j]
                lesson_id=tds[2].get_text().strip()
                # data={
                #     'lesson_manage_unit':lesson_manage_unit,
                #     'uk_lesson_id':lesson_id,
                #     'lesson_name':lesson_name,
                #     'lesson_credit':lesson_credit,
                #     'before_learning':before_learning,
                #     'lesson_open_turn':lesson_open_turn,
                #     'if_public_elective':True,
                #     'tags':tags,
                # }
                try:
                    for ta in tags:
                        try:
                            lab=LessonLabels.objects.create(lesson_id=lesson_id,label=ta)
                            print(lab)
                        except:
                            print('标签已存在')
                # self.__sebject_system_lesson.insert_one(data)
                # print(data)
                except:
                    print('公选课插入标签异常')
        '''
            __EVENTTARGET: ctl00$chdContent$SearchCourse1$lbt02
            __EVENTARGUMENT: 
            __VIEWSTATE: /wEPDwULLTE2ODQ4MDc2MTQPZBYCZg9kFgICAw9kFggCAQ8WAh4EVGV4dAUQMjAxOOW5tDEx5pyIOeaXpWQCAw8PFgIfAAUR5Ymp5L2Z77yaNDXliIbpkp9kZAIFDxYCHwAFGjIwMTYyNjcwMzA3OSDvvZwg5byg5pys6ImvZAILD2QWAgIBD2QWBgIBDxAPFgYeDURhdGFUZXh0RmllbGQFEuS4k+S4muenkeexu+WQjeensB4ORGF0YVZhbHVlRmllbGQFD+S4k+S4muenkeexu+WPtx4LXyFEYXRhQm91bmRnZBAVISvlk7LlrabnsbsgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgLOe7j+a1juWtpuexuyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgK+azleWtpuexuyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAs56S+5Lya5a2m57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAs5pS/5rK75a2m57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAs5pWZ6IKy5a2m57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAs5L2T6IKy5a2m57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAv5Lit5Zu96K+t6KiA5paH5a2m57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAv5aSW5Zu96K+t6KiA5paH5a2m57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAu5paw6Ze75Lyg5pKt5a2m57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAgICzljoblj7LlrabnsbsgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICvmlbDlrabnsbsgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgLOeJqeeQhuWtpuexuyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgK+WMluWtpuexuyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAt5Zyw55CG56eR5a2m57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgLeeUn+eJqeenkeWtpuexuyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC3mnZDmlpnnp5HlrabnsbsgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAs5b+D55CG5a2m57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAs57uf6K6h5a2m57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAt55S15rCU5L+h5oGv57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgLOiuoeeul+acuuexuyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgLuWMluW3peS4juWItuiNr+exuyAgICAgICAgICAgICAgICAgICAgICAgICAgICAr5bu6562R57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC3nlJ/nianlt6XnqIvnsbsgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAu5Z+O5Lmh6KeE5YiS5a2m57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAgIC3lt6XllYbnrqHnkIbnsbsgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAt5YWs5YWx566h55CG57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgMOeuoeeQhuenkeWtpuS4juW3peeoi+exuyAgICAgICAgICAgICAgICAgICAgICAgIDDnrqHnkIbnp5HlrabkuI7lt6XnqIsy57G7ICAgICAgICAgICAgICAgICAgICAgICAt55S15a2Q5ZWG5Yqh57G7ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgL+mfs+S5kOS4juiInui5iOWtpuexuyAgICAgICAgICAgICAgICAgICAgICAgICAgLee+juacr+iuvuiuoeexuyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICvoibrmnK/nsbsgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgFSEIMDEwMSAgICAIMDIwMSAgICAIMDMwMSAgICAIMDMwMyAgICAIMDMwNCAgICAIMDQwMSAgICAIMDQwMiAgICAIMDUwMSAgICAIMDUwMiAgICAIMDUwMyAgICAIMDYwMSAgICAIMDcwMSAgICAIMDcwMiAgICAIMDcwMyAgICAIMDcwNSAgICAIMDcxMCAgICAIMDcxMyAgICAIMDcxNSAgICAIMDcxNiAgICAIMDgwNyAgICAIMDgwOSAgICAIMDgxMSAgICAIMDgyOCAgICAIMDgzMCAgICAIMDgzMyAgICAIMTEwMiAgICAIMTEwMyAgICAIMTIwMSAgICAIMTIwMTIgICAIMTIwOCAgICAIMTMwMiAgICAIMTMwNCAgICAIMTMwNSAgICAUKwMhZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZGQCBQ8QDxYGHwEFDOWNleS9jeWQjeensB8CBQnljZXkvY3lj7cfA2dkEBUbEui0ouaUv+mHkeiejeWtpumZohLln47luILlu7rorr7lrabpmaIS5Yid562J5pWZ6IKy5a2m6ZmiDOS8oOaSreWtpumZohXlnLDnkIbkuI7njq/looPlrabpmaIS5Zu96ZmF5pWZ6IKy5a2m6ZmiEuWMluWtpuWMluW3peWtpumZohvorqHnrpfmnLrkv6Hmga/lt6XnqIvlrabpmaIS57un57ut5pWZ6IKy5a2m6ZmiDOaVmeiCsuWtpumZoh7lhpvkuovmlZnnoJTpg6jvvIjmraboo4Xpg6jvvIkS56eR5a2m5oqA5pyv5a2m6ZmiG+WOhuWPsuaWh+WMluS4juaXhea4uOWtpumZohXpqazlhYvmgJ3kuLvkuYnlrabpmaIM576O5pyv5a2m6ZmiEuWFjei0ueW4iOiMg+eUn+mZogzova/ku7blrabpmaIJ5ZWG5a2m6ZmiEueUn+WRveenkeWtpuWtpumZohvmlbDlrabkuI7kv6Hmga/np5HlrablrabpmaIM5L2T6IKy5a2m6ZmiD+WkluWbveivreWtpumZognmloflrabpmaIb54mp55CG5LiO6YCa5L+h55S15a2Q5a2m6ZmiDOW/g+eQhuWtpumZogzpn7PkuZDlrabpmaIM5pS/5rOV5a2m6ZmiFRsINjgwMDAgICAINjMwMDAgICAIODIwMDAgICAINjQwMDAgICAINDgwMDAgICAINjkwMDAgICAINjEwMDAgICAINjIwMDAgICAINDUwICAgICAINTAwMDAgICAIMzcwMDAgICAIODEwMDAgICAINTgwMDAgICAINDYwMDAgICAINjUwMDAgICAINTcwMDAgICAINjcwMDAgICAINTQwMDAgICAINjYwMDAgICAINTUwMDAgICAINTYwMDAgICAINTIwMDAgICAINTEwMDAgICAINjAwMDAgICAINDkwMDAgICAINTMwMDAgICAINTkwMDAgICAUKwMbZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZGQCGw88KwARAgEQFgAWABYADBQrAABkGAEFKGN0bDAwJGNoZENvbnRlbnQkU2VhcmNoQ291cnNlMSRndkNvbnRlbnQPZ2RVBXfHFrwgtFSiXV3LPfr7DUbhVnhCDKmuta7c8dXn9Q==
            __VIEWSTATEGENERATOR: E8154CE2
            __EVENTVALIDATION: /wEdAEdyEiQExmndMOyitHdRbWDIetmnXCW78O8MOJUYt92SyVC2tGXOYPidFVNO3VzPXSzm1UlNGib8bZo5pu4qoXWwxxwKCMz0aUlIbNoRlXpBsSqQ0j4YSbTDnCgRTalURiOzhstengVnH63ZQuUbFdr7B9BkAeanUv7HfMsvesAMEjmgQrMYtHYyYaQWTmPTmFSihoCQunl4QgbYPdTgGZRI6altXLOalZ+3l5UkdnwX9uwfopkHfKCaLM2+hrAN6HxnfMN5w0+SLQUeYxa0s6pqAbXpfoiRG8NKL5LyZXyY7oABd6Mx16etLVZ8YXmq6BbSECi0a2yROUlIavFhqXq+edJMPM9GPjeTHTWv5In1nEIStOp96/emy4nfzt6c5c5+L7XPcUKCR+izZwP8ZiqkfHLGI40bg2UgMFf2u8HxY44cl2WKsC0Es/R0WbezqqG4Euu45LeskjQpweN5zMBT07yUNwl+o2SMyJeuh8YgUhCrF8THnG5SQ26iKeKDxnkB15jd+hVv4z8VWZGMBova6dWv/NKrlHyHST3IoUTnHw5CMZyRpif/mXqTQcU2RWx0sJiWyr+6mTtxcDxLkPPWhCrCePSBm3B2jCkRqfBTFsFZzkH7qx8JN5eKMc32f4EOxBHWvUqfpk9SzNBExt8srRop7L5BTclaA6lGYxmHN+jfcBkPcM7e19flSqf5wcvdfMq+RgdW0gxF+gtpZgAoqdl5WZsBeI+0hB/YjjadQNe2OGnIO05jyg6TD1oQdsEWjznsK05hYKqT1+6iD4876x/oWGtmGOsOttJeDIzztg42vAm2JPqfJotyk5q5k0EMqw6t6npinpGIZdyDd5/6+so6oJRXtvg8MuuPelVvY8xeAA8O6Ot0zV4hDnJG3oINHaVqU26FgG2Wj745l+h7o8dKdecn3exi3lHPhojHt+4fu9B9lu3ul/lN/S5IZb3lnq6VAhFrIjHoZdF943Q3rZ8V1muVcPo1klqmh+Nk+sywF7I9b9oAzmx/9xMeYNwD7gPKacwgWlxfzYXlGH5mSc7gcETTVVief1eaAVFYDWW1dZYW85Yng3EI3BnLNUHXAj5eV52HeD8+fGeh7Ntt4nRLilwe2CxXkghBVM+xcRA23szaIlletUs6FwUhQo7uOjPUisz0Uw8WEST22Ygon0oCGQqARASLWtmAcQS0z2PG0Ptnj6S1u2dAXz1OXbZ1yPD2z0z8GxxFYgvDZgEr1pSHD03pQ5zMo8O5KtAsa1xO+8AQOkFXqQ3UWZkn24xU7GcpVAeYPXY38nXaYX+bd4iGVmP1EwNkkRgcuabOFe4x99aOHClDTVfYNQ41mHExRV5GQOOAHnPZHX2T6VVEiz7Af6ISt2PNKJ2IH4Wqwwk6QrssLGuR4G1MULncO1UC3qGXlk4K0eyl+RtLjZO1eTLiOCZdwy9SxgAzRpdhRgk8ybUPQC65hOnXLlG5qLsevRN/0nMKCFqUWxQw/mjFn96ZHXg5KwyvqDRBujIPjjMxRk+scUiSgcpcaYvUJ/RzY75CrAxCtegbHzk1Zrfh
            ctl00$chdContent$SearchCourse1$ddlXkml: 0101    
            ctl00$chdContent$SearchCourse1$ddlDW: 68000   
            ctl00$chdContent$SearchCourse1$txtKey: 
        '''

    def __fenci(self,st):
        words=jieba.cut(st,cut_all=True)
        word_list=[]
        for wo in words:
            if len(wo)>=2:
                try:
                    int(wo)
                except:
                    if wo[0]!='u':
                        word_list.append(wo)
        return word_list

    def __get_lesson_from_lesson_subject_category(self):
        url='http://xk.jxnu.edu.cn/Step1/AddCourseSearch.aspx'
        wb_data=self.__session.get(url)
        soup=BeautifulSoup(wb_data.text,'html5lib')
        subject_categorys=soup.select('#ctl00_chdContent_SearchCourse1_ddlXkml > option')
        hid_data=self.__get_hid_data(url)
        for subject_category in subject_categorys:
            post_data={
                '__EVENTTARGET':'',
                '__EVENTARGUMENT':'',
                '__VIEWSTATE':hid_data[0],
                '__VIEWSTATEGENERATOR':hid_data[1],
                '__EVENTVALIDATION':hid_data[2],
                'ctl00$chdContent$SearchCourse1$ddlXkml':subject_category.get('value'),
                'ctl00$chdContent$SearchCourse1$btnSearch1':'查询',
                'ctl00$chdContent$SearchCourse1$ddlDW':'68000   ',
                'ctl00$chdContent$SearchCourse1$txtKey':''
            }
            web_data=self.__session.post(url=url,data=post_data)
            soup2=BeautifulSoup(web_data.text,'html5lib')
            trs = soup2.select('#ctl00_chdContent_SearchCourse1_gvContent > tbody > tr')
            # print(trs)
            for tr in trs[1:]:
                tds = tr.select('td')

                lesson_manage_unit = tds[1].get_text().strip()
                if lesson_manage_unit in ['', '无','None']:
                    lesson_manage_unit = None
                else:
                    pass
                uk_lesson_id=tds[2].get_text().strip()
                try:
                    lesson_open_turn = int(tds[6].get_text().strip().strip('每学年第学期').strip())
                except:
                    lesson_open_turn = None
                try:
                    lesson_credit = int(tds[4].get_text().strip())
                except:
                    lesson_credit = 2
                before_learning = tds[5].get_text().strip()
                if before_learning not in ['', '无', 'None']:
                    pass
                else:
                    before_learning = None
                subject_category_name=subject_category.get_text().strip()
                try:
                    lesson_name = tds[3].get_text().strip()
                except:
                    lesson_name = None

                if lesson_name != None:
                    tags = self.__fenci(lesson_name)
                    if lesson_manage_unit != None:
                        tags.append(lesson_manage_unit)
                        tags.append(subject_category_name)
                        tags = set(tags)
                        tags = list(tags)
                else:
                    if lesson_manage_unit != None:
                        tags = [lesson_manage_unit]
                    else:
                        tags=None
                # data = {
                #     'lesson_manage_unit': lesson_manage_unit,
                #     'uk_lesson_id': uk_lesson_id,
                #     'lesson_name': lesson_name,
                #     'lesson_credit': lesson_credit,
                #     'before_learning': before_learning,
                #     'lesson_open_turn': lesson_open_turn,
                #     'if_public_elective': False,
                #     'tags': tags,
                # }
                try:
                    for ta in tags:
                        try:
                            lab=LessonLabels.objects.create(lesson_id=uk_lesson_id,label=ta)
                            print(lab)
                        except:
                            print('标签已存在')

                    # self.__sebject_system_lesson.insert_one(data)
                    # print(data)
                except:
                    # id={'uk_lesson_id':uk_lesson_id}
                    # the_data=self.__sebject_system_lesson.find_one(id)
                    # the_data['tags'].append(subject_category_name)
                    # result=self.__sebject_system_lesson.update_one(id,{'$set':the_data})
                    # print(result)
                    print('按学科种类爬课程，标签插入异常')


    def __get_lesson_from_colloge(self):
        url='http://xk.jxnu.edu.cn/Step1/AddCourseSearch.aspx'
        wb_data=self.__session.get(url)
        soup=BeautifulSoup(wb_data.text,'html5lib')
        colloges=soup.select('#ctl00_chdContent_SearchCourse1_ddlDW > option')
        hid_data=self.__get_hid_data(url)
        for colloge in colloges:
            colloge_id=colloge.get('value')
            colloge_name=colloge.get_text().strip()
            form_data={
                '__EVENTTARGET':'',
                '__EVENTARGUMENT':'',
                '__VIEWSTATE':hid_data[0],
                '__VIEWSTATEGENERATOR':hid_data[1],
                '__EVENTVALIDATION':hid_data[2],
                'ctl00$chdContent$SearchCourse1$ddlXkml':'0101    ',
                'ctl00$chdContent$SearchCourse1$ddlDW':colloge_id,
                'ctl00$chdContent$SearchCourse1$btnSearch2':'查询',
                'ctl00$chdContent$SearchCourse1$txtKey':''
            }
            wb_data=self.__session.post(url=url,data=form_data)
            soup=BeautifulSoup(wb_data.text,'html5lib')

            trs = soup.select('#ctl00_chdContent_SearchCourse1_gvContent > tbody > tr')
            # print(trs)
            for tr in trs[1:]:
                tds = tr.select('td')
                lesson_manage_unit = tds[1].get_text().strip()
                if lesson_manage_unit in ['', '无','None']:
                    lesson_manage_unit = None
                else:
                    pass
                uk_lesson_id = tds[2].get_text().strip()
                try:
                    lesson_open_turn = int(tds[6].get_text().strip().strip('每学年第学期').strip())
                except:
                    lesson_open_turn = None
                try:
                    lesson_credit = int(tds[4].get_text().strip())
                except:
                    lesson_credit = 2
                before_learning = tds[5].get_text().strip()
                if before_learning not in ['', '无', 'None']:
                    pass
                else:
                    before_learning = None
                try:
                    lesson_name = tds[3].get_text().strip()
                except:
                    lesson_name = None

                if lesson_name not in [None,'']:
                    tags = self.__fenci(lesson_name)
                    if lesson_manage_unit != None:
                        tags.append(lesson_manage_unit)
                        tags = set(tags)
                        tags = list(tags)
                else:
                    if lesson_manage_unit != None:
                        tags = [lesson_manage_unit]
                    else:
                        tags = None
                data = {
                    'lesson_manage_unit': lesson_manage_unit,
                    'uk_lesson_id': uk_lesson_id,
                    'lesson_name': lesson_name,
                    'lesson_credit': lesson_credit,
                    'before_learning': before_learning,
                    'lesson_open_turn': lesson_open_turn,
                    'if_public_elective': False,
                    'tags': tags,
                }
                try:
                    for ta in tags:
                        try:
                            lab=LessonLabels.objects.create(lesson_id=uk_lesson_id,label=ta)
                            print(lab)
                        except:
                            print('标签已存在')
                    # self.__sebject_system_lesson.insert_one(data)
                    print(data)
                except:
                    print('按学院爬标签，异常，可能已存在')


    #调用三个方法 获取所有课程的方法
    def get_lesson(self):
        self.__get_public_elective()
        self.__get_lesson_from_lesson_subject_category()
        self.__get_lesson_from_colloge()

    def elective_course(self):
        url='http://xk.jxnu.edu.cn/Step1/AddCourse.aspx?kch=002152'

        '''
        __EVENTTARGET: ctl00$chdContent$gvContent$ctl02$btn
        __EVENTARGUMENT: 
        __VIEWSTATE: /wEPDwUJNDk0MDM2MjkwD2QWAmYPZBYCAgMPZBYIAgEPFgIeBFRleHQFETIwMTjlubQxMeaciDEw5pelZAIDDw8WAh8ABRHliankvZnvvJo1OeWIhumSn2RkAgUPFgIfAAUaMjAxNjI2NzAzMDc5IO+9nCDlvKDmnKzoia9kAgsPZBYGZg8WAh8ABS3jgJDns7vnu5/mj5DnpLrjgJHor77nqIvmgKfotKjvvJrlhazlhbHpgInkv65kAgEPPCsAEQMADxYEHgtfIURhdGFCb3VuZGceC18hSXRlbUNvdW50AgFkARAWAQIFFgE8KwAFAQAWAh4HVmlzaWJsZWcWAQIGDBQrAAAWAmYPZBYEAgEPZBYMZg9kFgJmDxUBATFkAgEPDxYCHwAFDOS8oOaSreWtpumZomRkAgIPDxYCHwAFCjAwMzYwMSAgICBkZAIDD2QWAmYPFQFZPGEgY2xhc3M9J2J0biBidG4tbWluaSBidG4tcHJpbWFyeScgaHJlZj0jIG9uY2xpY2s9InZpZXdUZWFjaGVyKCcwMDM2MDEnKTsiPuS9leW9pOWuhzwvYT5kAgQPDxYCHwAFA+eUt2RkAgUPZBYEZg8VAQBkAgEPDxYCHg9Db21tYW5kQXJndW1lbnQFBjAwMzYwMWRkAgIPDxYCHwNoZGQCAg8WAh8ABQIwMWQYAQUaY3RsMDAkY2hkQ29udGVudCRndkNvbnRlbnQPPCsADAEIAgFkg8fGX7xTO+fNDXYs1d2Ls4jRY9K7R7M1sNFhptGcmHU=
        __VIEWSTATEGENERATOR: 2E10D4E0
        __EVENTVALIDATION: /wEdAAOcCGU65tjK6QemDrfbY+xQetmnXCW78O8MOJUYt92SyeIK2/a1lSKBikexV1MOTBJcaYapqG+6r1p2pvUmNd+YED0Fe0OmAkrJzHRYXmYquA==
        '''

    def set_lesson_point(self):
        url='http://xk.jxnu.edu.cn/Step1/SetXuandian.aspx?kch=002152'

        '''
        __EVENTTARGET: ctl00$chdContent$txtXuandian
        __EVENTARGUMENT: 
        __LASTFOCUS: 
        __VIEWSTATE: /wEPDwUKLTgxMDAyMDYzOA9kFgJmD2QWAgIDD2QWCAIBDxYCHgRUZXh0BREyMDE45bm0MTHmnIgxMOaXpWQCAw8PFgIfAAUR5Ymp5L2Z77yaNTXliIbpkp9kZAIFDxYCHwAFGjIwMTYyNjcwMzA3OSDvvZwg5byg5pys6ImvZAILD2QWBgIBDxYCHwAFQOivvueoi+WPt++8mjAwMjE1MiAgICAgICDor77nqIvlkI3np7DvvJrkupLogZTnvZHkuI7lm73pmYXlhbPns7tkAgMPDxYCHwAFATBkZAIHDxYCHwAFAzEwMGRkTw2faXahhZmwjl422u+LO+PSDNt3FzVV1w80uRvZZxs=
        __VIEWSTATEGENERATOR: 0D844D4D
        __EVENTVALIDATION: /wEdAATv7qOBl5TOJMInvQJnTe6XetmnXCW78O8MOJUYt92SyZK6QK8fLNki86IskmwvIifNeYHLviHX1rdPR0mMeuwktjGQ3SkUgTwNW5hKob0ynJE1FSjgKolWYjCEMQ19CvA=
        ctl00$chdContent$txtXuandian: 1
        ctl00$chdContent$btnSet: 确定
        '''

    def __get_lesson_to_delete(self):
        url='http://xk.jxnu.edu.cn/Step1/Default.aspx'
        headers={
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        }
        wb_data=self.__session.get(url=url,headers=headers)
        soup=BeautifulSoup(wb_data.text,'html5lib')
        # lesson_name=soup.select('#ctl00_chdContent_gvContent > tbody > tr:nth-of-type(2) > td:nth-of-type(3)')[0].get_text()
        trs=soup.select('#ctl00_chdContent_gvContent > tbody > tr')
        list=[]
        for tr in trs[1:]:
            try:
                tds=tr.select('td')
                data={
                    'lesson_id':tds[1].get_text().strip(),
                    'lesson_name':tds[2].get_text().strip(),
                    'delete_id':tds[6].select('input')[0].get('id')
                }
                list.append(data)
            except:
                pass
        print(list)


    def delete_lesson(self,delete_id):
        url = 'http://xk.jxnu.edu.cn/Step1/Default.aspx'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        }
        del_id=delete_id.replace('_','$')
        hid_data=self.__get_hid_data(url)
        post_data={
            '__EVENTTARGET': '',
            '__EVENTARGUMENT':'',
            '__VIEWSTATE':hid_data[0],
            '__VIEWSTATEGENERATOR':hid_data[1],
            '__EVENTVALIDATION':hid_data[2],
            del_id: '删除课程',
        }
        wb_data=self.__session.post(url=url,data=post_data)
        soup=BeautifulSoup(wb_data.text,'html5lib')
        print(soup)





        '''
        __EVENTTARGET: 
        __EVENTARGUMENT: 
        __VIEWSTATE: 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
        __VIEWSTATEGENERATOR: 15987359
        __EVENTVALIDATION: /wEdAAfYKZ1I+zdnGq9JdCxqc4GhetmnXCW78O8MOJUYt92Syd4Dpk7uptH9pM9W0hpkHiTk/MORvM7cQVU9dXx+7JnlhuCElKSEi/kdbiZLmIAuHCJSwfZqK1iVamEZNVdq0JLsOeXZa9CbhFgYQbb7SWIiTFNQYcIF91GPZQTbKUO2AR3hias91lDIlgh7N4RVpb8=
        ctl00$chdContent$gvContent$ctl03$btnDelete: 删除课程
        '''


class XuanKe:
    def __init__(self,student_id=MY_USERNAME,student_password=MY_WORD):
        # self.__client=pymongo.MongoClient(host="localhost",port=27017,connect=False)
        # self.__sebject_system=self.__client['xzs_spider_subject_system']
        # self.__sebject_system.authenticate(name='xzs_spider_subject_system_user',password='xsssum2567076458')
        # self.__sebject_system_lesson = self.__sebject_system['sebject_system_lesson']
        # self.__sebject_system_lesson.create_index([('uk_lesson_id', 1)], unique=True)

        self.student_id=student_id
        self.student_password=student_password
        self.__session=requests.Session()
        self.next_semester = NextSemester.objects.first().next_semester

    # 取出表单隐藏值的私有方法
    def __get_hid_data(self, url):
        # 先get请求一次
        wb_data = self.__session.get(url)
        soup = BeautifulSoup(wb_data.text, 'lxml')
        # 从get请求后反馈的response中找出两个隐藏值
        __VIEWSTATE = soup.select("input[name='__VIEWSTATE']")[0].get('value')
        __VIEWSTATEGENERATOR = soup.select("input[name='__VIEWSTATEGENERATOR']")[0].get('value')
        __EVENTVALIDATION = soup.select("input[name='__EVENTVALIDATION']")[0].get('value')
        # 返回两个隐藏值
        return __VIEWSTATE,__VIEWSTATEGENERATOR,__EVENTVALIDATION

    def login(self):
        url='http://xk.jxnu.edu.cn/default.aspx'
        hid_data=self.__get_hid_data(url)
        post_data={
            '__VIEWSTATE':hid_data[0],
            '__VIEWSTATEGENERATOR':hid_data[1],
            '__EVENTVALIDATION':hid_data[2],
            'txtUserNum':self.student_id,
            'txtPassword':self.student_password,
            'btnLogin':'登录'
        }
        wb_data=self.__session.post(url=url,data=post_data)
        soup=BeautifulSoup(wb_data.text,'html5lib')
        name=soup.select('#ctl00_lbtExit')[0].previousSibling.split('｜')[1].strip()
        print(name+' 登录成功\n')

    def get_lesson_teacher(self,kch):
        url='http://xk.jxnu.edu.cn/Step1/AddCourse.aspx?kch=%s'%kch
        wb_data=self.__session.get(url)
        soup=BeautifulSoup(wb_data.text,'html5lib')
        print(soup)

        # wb_data=self.
    def get_lesson_information(self,kch,step='1',timeout=4,limit_time=5):
        try:
            url='http://xk.jxnu.edu.cn/Step{0}/AddCourse.aspx?kch={1}'.format(step,kch)
            wb_data=self.__session.get(url=url,timeout=timeout)
            if wb_data.status_code==requests.codes.ok:
                soup=BeautifulSoup(wb_data.text,'html5lib')
                try:
                    admin_department=soup.select('div.box-content > table > tbody > tr:nth-of-type(2) > td:nth-of-type(4)')[0].get_text().strip()
                    open_semester=soup.select('div.box-content > table > tbody > tr:nth-of-type(3) > td:nth-of-type(2)')[0].get_text().strip()
                    before_learning_text=soup.select('div.box-content > table > tbody > tr:nth-of-type(4) > td:nth-of-type(2)')[0].get_text().strip()
                    profile=soup.select('div.box-content > table > tbody > tr:nth-of-type(5) > td:nth-of-type(2)')[0].get_text().strip()
                    data={'admin_department':admin_department,'open_semester':open_semester,'before_learning_text':before_learning_text,'profile':profile}
                    print(data)
                    return data
                except:
                    print('css selector error')
                    return None
            else:
                return None
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_lesson_information timeout, retrying。。')
                return self.get_lesson_information(kch=kch,step=step,limit_time=limit_ti)
            else:
                return None

    def get_one_step1_lesson_teacher_list(self,kch,soup=None,timeout=4,limit_time=4):
        if not soup:
            try:
                next_semester=self.next_semester
                url = 'http://xk.jxnu.edu.cn/Step1/AddCourse.aspx?kch={0}'.format(kch)
                wb_data = self.__session.get(url=url, timeout=timeout)
                if wb_data.status_code == requests.codes.ok:
                    soup = BeautifulSoup(wb_data.text, 'html5lib')
                    trs=soup.select('#ctl00_chdContent_gvContent > tbody > tr')
                    if len(trs)>1:
                        iii=2
                        lis=[]
                        for tr in trs[1:]:
                            tds=tr.select('td')
                            teacher_id=tds[2].get_text().strip()
                            # print(iii)
                            if iii<10:
                                post_code='ctl00$chdContent$gvContent$ctl0{0}$btn'.format(str(iii))
                            else:
                                post_code = 'ctl00$chdContent$gvContent$ctl{0}$btn'.format(str(iii))
                            iii=iii+1
                            st=StepOneLessonTeacher.objects.filter(teacher_id=teacher_id,semester=next_semester,lesson_id=kch)
                            if not st:
                                try:
                                    StepOneLessonTeacher.objects.create(teacher_id=teacher_id,semester=next_semester,lesson_id=kch,post_code=post_code)
                                    print('创建成功')
                                except:
                                    print('step_one_lesson_teacher创建失败')
                            else:
                                ssst=st.filter(post_code=post_code)
                                if ssst:
                                    print('该学期该课程该编号已存在老师')
                                else:
                                    st[0].teacher_id=teacher_id
                                    st[0].save()
                                    print('教师变动，已更新')
                            data = {'teacher_id': teacher_id, 'semester': next_semester, 'lesson_id': kch,'post_code': post_code}
                            lis.append(data)
                        return lis
                                # return {'teacher_id':teacher_id,'semester':next_semester,'lesson_id':kch}
                    else:
                        print('未找到教师，可能该学期不开课')
                        return None
            except:
                limit_ti = limit_time - 1
                if limit_ti > 0:
                    print('get_one_step1_lesson_teacher_list timeout, retrying。。')
                    return self.get_one_step1_lesson_teacher_list(kch=kch,limit_time=limit_ti)
                else:
                    return None
        else:
            trs = soup.select('#ctl00_chdContent_gvContent > tbody > tr')
            if len(trs) > 1:
                iii = 2
                lis = []
                for tr in trs[1:]:
                    tds = tr.select('td')
                    teacher_id = tds[2].get_text().strip()
                    # print(iii)
                    if iii < 10:
                        post_code = 'ctl00$chdContent$gvContent$ctl0{0}$btn'.format(str(iii))
                    else:
                        post_code = 'ctl00$chdContent$gvContent$ctl{0}$btn'.format(str(iii))
                    iii = iii + 1
                    # st = StepOneLessonTeacher.objects.filter(teacher_id=teacher_id, semester=self.next_semester,lesson_id=kch)
                    # if not st:
                    try:
                        StepOneLessonTeacher.objects.create(teacher_id=teacher_id, semester=self.next_semester,lesson_id=kch, post_code=post_code)
                        print('创建成功')
                    except:
                        print('step_one_lesson_teacher创建失败')
                    # else:
                    #     ssst = st.filter(post_code=post_code)
                    #     if ssst:
                    #         print('该学期该课程该编号已存在老师')
                    #     else:
                    #         st[0].teacher_id = teacher_id
                    #         st[0].save()
                    #         print('教师变动，已更新')
                    data = {'teacher_id': teacher_id, 'semester': self.next_semester, 'lesson_id': kch,'post_code': post_code}
                    lis.append(data)
                return lis
                # return {'teacher_id':teacher_id,'semester':next_semester,'lesson_id':kch}
            else:
                print('未找到教师，可能该学期不开课')
                return None

    def get_all_step1_lesson_teacher_list(self):
        lessons=Lesson.objects.all()
        for less in lessons:
            self.get_one_step1_lesson_teacher_list(kch=less.id)

    def __get_xuanke_hid_data(self,url,timeout=4,limit_time=4):
        try:
            # 先get请求一次
            wb_data = self.__session.get(url)
            soup = BeautifulSoup(wb_data.text, 'lxml')
            # 从get请求后反馈的response中找出两个隐藏值
            __VIEWSTATE = soup.select("input[name='__VIEWSTATE']")[0].get('value')
            __VIEWSTATEGENERATOR = soup.select("input[name='__VIEWSTATEGENERATOR']")[0].get('value')
            __EVENTVALIDATION = soup.select("input[name='__EVENTVALIDATION']")[0].get('value')
            __VIEWSTATEGENERATOR = soup.select("input[name='__VIEWSTATEGENERATOR']")[0].get('value')
            # 返回两个隐藏值
            return __VIEWSTATE, __VIEWSTATEGENERATOR, __EVENTVALIDATION,__VIEWSTATEGENERATOR
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('get_xuanke_hid_data timeout, retrying。。')
                return self.__get_xuanke_hid_data(url=url,timeout=timeout,limit_time=limit_ti)
            else:
                return None

    def xuanke(self,kch,post_data,teacher_id,timeout=4,limit_time=4):
        try:
            url=r'http://xk.jxnu.edu.cn/Step1/addcourse.aspx?kch=%s'%kch
            wb_data = self.__session.get(url)
            soup = BeautifulSoup(wb_data.text, 'html5lib')
            # 从get请求后反馈的response中找出两个隐藏值
            __VIEWSTATE = soup.select("input[name='__VIEWSTATE']")[0].get('value')
            __VIEWSTATEGENERATOR = soup.select("input[name='__VIEWSTATEGENERATOR']")[0].get('value')
            __EVENTVALIDATION = soup.select("input[name='__EVENTVALIDATION']")[0].get('value')
            __VIEWSTATEGENERATOR = soup.select("input[name='__VIEWSTATEGENERATOR']")[0].get('value')
            trs=soup.select("#ctl00_chdContent_gvContent > tbody > tr")
            if len(trs)>1:
                for tr in trs[1:]:
                    tds=tr.select('td')
                    the_teacher_id=tds[2].get_text().strip()
                    if the_teacher_id==teacher_id:
                        a=tds[5].select('a')
                        if a:
                            code=a[0].get('href').split("'")[1]
                            if code != post_data:
                                StepOneLessonTeacher.objects.filter(semester=self.next_semester,lesson_id=kch).delete()
                                self.get_one_step1_lesson_teacher_list(kch=kch,soup=soup)
                            '''
                            __EVENTTARGET: ctl00$chdContent$gvContent$ctl02$btn
                            __EVENTARGUMENT: 
                            __VIEWSTATE: /wEPDwUJNDk0MDM2MjkwD2QWAmYPZBYCAgMPZBYIAgEPFgIeBFRleHQFDzIwMTnlubQ15pyIOeaXpWQCAw8PFgIfAAUR5Ymp5L2Z77yaMzTliIbpkp9kZAIFDxYCHwAFGjIwMTYyNjcwMzA3OSDvvZwg5byg5pys6ImvZAILD2QWBmYPFgIfAAUt44CQ57O757uf5o+Q56S644CR6K++56iL5oCn6LSo77ya5LiT5Lia6ZmQ6YCJZAIBDzwrABEDAA8WBB4LXyFEYXRhQm91bmRnHgtfIUl0ZW1Db3VudAIBZAEQFgECBRYBPCsABQEAFgIeB1Zpc2libGVnFgECBgwUKwAAFgJmD2QWBAIBD2QWDGYPZBYCZg8VAQExZAIBDw8WAh8ABQzova/ku7blrabpmaJkZAICDw8WAh8ABQowMDM5NjcgICAgZGQCAw9kFgJmDxUBVjxhIGNsYXNzPSdidG4gYnRuLW1pbmkgYnRuLXByaW1hcnknIGhyZWY9IyBvbmNsaWNrPSJ2aWV3VGVhY2hlcignMDAzOTY3Jyk7Ij7pvprkv4o8L2E+ZAIEDw8WAh8ABQPnlLdkZAIFD2QWBGYPFQEAZAIBDw8WAh4PQ29tbWFuZEFyZ3VtZW50BQYwMDM5NjdkZAICDw8WAh8DaGRkAgIPFgIfAAUCMDVkGAEFGmN0bDAwJGNoZENvbnRlbnQkZ3ZDb250ZW50DzwrAAwBCAIBZGfe8ZsjhhD3xOBmz+0swUJwzt1dhknix345VZ8eus2j
                            __VIEWSTATEGENERATOR: 2E10D4E0
                            __EVENTVALIDATION: /wEdAANIHsQgR6jaKJ/AiXerR7k0etmnXCW78O8MOJUYt92SyeIK2/a1lSKBikexV1MOTBKFA4KHQ8VBx8kRomN02igD6gjGXcg5rQhaPGnUz0k2SQ==
                            '''
                            data={
                                '__EVENTTARGET':post_data,
                                '__EVENTARGUMENT':'',
                                '__VIEWSTATE':__VIEWSTATE,
                                '__VIEWSTATEGENERATOR':__VIEWSTATEGENERATOR,
                                '__EVENTVALIDATION':__EVENTVALIDATION,
                            }
                            wb_data=self.__session.post(url,data=data,timeout=timeout)
                            print(wb_data.text)
                            if wb_data.status_code==requests.codes.ok:
                                return True
                            else:
                                return None
                        else:
                            self.get_one_step1_lesson_teacher_list(kch=kch, soup=soup)
                            return None
                    else:
                        pass
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('xuanke timeout, retrying。。')
                return self.xuanke(kch=kch, limit_time=limit_ti)
            else:
                return None


    def set_xuandian(self,kch,xd,timeout=4,limit_time=4):
        try:
            url=r'http://xk.jxnu.edu.cn/Step1/SetXuandian.aspx?kch=%s'%kch
            hid_data=self.__get_hid_data(url)
            data={
                '__LASTFOCUS':'',
                '__EVENTTARGET':'ctl00$chdContent$txtXuandian',
                '__EVENTARGUMENT':'',
                '__VIEWSTATE':hid_data[0],
                '__VIEWSTATEGENERATOR':hid_data[1],
                '__EVENTVALIDATION':hid_data[2],
                'ctl00$chdContent$txtXuandian':xd,
                'ctl00$chdContent$btnSet':'确定'
            }
            wb_data=self.__session.post(url=url,data=data,timeout=timeout)
            if wb_data.status_code==requests.codes.ok:
                # print(wb_data.text)
                return True
            else:
                return None
            # '''
            # __LASTFOCUS:
            # __EVENTTARGET: ctl00$chdContent$txtXuandian
            # __EVENTARGUMENT:
            # __VIEWSTATE: /wEPDwUKLTgxMDAyMDYzOA9kFgJmD2QWAgIDD2QWCAIBDxYCHgRUZXh0BQ8yMDE55bm0NeaciDnml6VkAgMPDxYCHwAFEeWJqeS9me+8mjM25YiG6ZKfZGQCBQ8WAh8ABRoyMDE2MjY3MDMwNzkg772cIOW8oOacrOiJr2QCCw9kFggCAQ8WAh8ABTTor77nqIvlj7fvvJowMDIwMDkgICAgICAg6K++56iL5ZCN56ew77ya5aSn5a2m6K+t5paHZAIDDw8WAh8AZWRkAgcPFgIfAAUDMTAwZAIJDxYCHwAFMzxkaXYgY2xhc3M9J2FsZXJ0IGFsZXJ0LWluZm8nPuivt+i+k+WFpeWAvO+8gTwvZGl2PmRkOVq3cEEa549GHL6SKTmP3rGs/AnZOqwlSm051+WI9GY=
            # __VIEWSTATEGENERATOR: 0D844D4D
            # __EVENTVALIDATION: /wEdAASJlYRoINFD7vC9DQKyA7YbetmnXCW78O8MOJUYt92SyZK6QK8fLNki86IskmwvIifNeYHLviHX1rdPR0mMeuwktbkcNHsss4FMlENeNnPvfdMChbYmrjR1UyDhXQHvIUk=
            # ctl00$chdContent$txtXuandian: 100
            # ctl00$chdContent$btnSet: 确定
            # '''
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('set_xuandian timeout, retrying。。')
                return self.set_xuandian(kch=kch,xd=xd,limit_time=limit_ti,timeout=timeout)
            else:
                return None

    def get_xuanke_page(self,timeout=4,limit_time=4):
        try:
            url=r'http://xk.jxnu.edu.cn/Step1/Default.aspx'
            wb_data=self.__session.get(url,timeout=timeout)
            next_semester = self.next_semester
            soup=BeautifulSoup(wb_data.text,'html5lib')
            trs=soup.select('#ctl00_chdContent_gvContent > tbody > tr')
            if len(trs)>1:
                for tr in trs[1:]:
                    tds=tr.select('td')
                    teacher_id = tds[5].select('a')[0].get('onclick').split("'")[1]
                    lesson_id=tds[1].get_text().strip()
                    lesson_type=tds[4].get_text().strip()
                    input=tds[6].select('input')
                    if input:
                        input=input[0]
                        delete_post_code=input.get('name')
                    else:
                        delete_post_code=''
                    a=tds[7].select('a')
                    if a:
                        try:
                            point=int(a[0].previous_sibling.strip())
                        except:
                            point=0
                    else:
                        point=0
                    step_one_lesson_teacher=StepOneLessonTeacher.objects.filter(lesson_id=lesson_id,teacher_id=teacher_id,semester=next_semester)
                    if step_one_lesson_teacher:
                        try:
                            my_xuanke=MyXuanKe.objects.create(student_id=self.student_id,lesson_type=lesson_type,lesson_teacher=step_one_lesson_teacher[0],point=point,delete_post_code=delete_post_code)
                            print(my_xuanke)
                        except:
                            print('my_xuanke已存在')
                    else:
                        try:
                            step_one_lesson_teacher=StepOneLessonTeacher.objects.create(teacher_id=teacher_id,lesson_id=lesson_id,semester=next_semester,can_delete=False)
                            try:
                                my_xuanke = MyXuanKe.objects.create(student_id=self.student_id, lesson_type=lesson_type,lesson_teacher=step_one_lesson_teacher[0], point=point)
                                print(my_xuanke)
                            except:
                                print('my_xuanke创建失败')
                        except:
                            print('新建StepOneLessonTeacher失败')
            else:
                return None
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('set_xuandian timeout, retrying。。')
                return self.get_xuanke_page(limit_time=limit_ti, timeout=timeout)
            else:
                return None

    def clean_xuanke_page(self):
        next_semester = self.next_semester
        try:
            MyXuanKe.objects.filter(student_id=self.student_id,lesson_teacher__semester=next_semester).delete()
            print('清除成功！')
        except:
            print('清除失败！')


    def delete_lesson(self,kch,timeout=4,limit_time=4):
        try:
            url='http://xk.jxnu.edu.cn/Step1/Default.aspx'
            hid_data=self.__get_hid_data(url)
            '''
            __EVENTTARGET: 
            __EVENTARGUMENT: 
            __VIEWSTATE: /wEPDwUKMTAzMTkxMjY0NA9kFgJmD2QWAgIDD2QWCAIBDxYCHgRUZXh0BRAyMDE55bm0NeaciDEw5pelZAIDDw8WAh8ABRHliankvZnvvJoyOOWIhumSn2RkAgUPFgIfAAUaMjAxNjI2NzAzMDc5IO+9nCDlvKDmnKzoia9kAgsPZBYEAgEPFgIfAAVx5b2T5YmN6K++56iL5oC75a2m5YiG77yaN++8iOWFgeiuuOWtpuWIhjE1IC0gMzDliIYo5pmu6YCaKe+8ie+8myAgICDmiJHnmoTpgInngrnvvJoxMDDvvIjlt7LnlKjvvJozMCzlj6/nlKjvvJo3MClkAgMPPCsAEQMADxYEHgtfIURhdGFCb3VuZGceC18hSXRlbUNvdW50AgJkARAWABYAFgAMFCsAABYCZg9kFgYCAQ9kFhBmD2QWAmYPFQEBMWQCAQ8PFgIfAAUKMDAyMDA5ICAgIGRkAgIPZBYCZg8VAVU8YSB0aXRsZT0n5p+l55yL6K++56iL5L+h5oGvJyBocmVmPSMgb25jbGljaz0idmlld0NvdXJzZSgnMDAyMDA5Jyk7Ij7lpKflrabor63mloc8L2E+ZAIDDw8WAh8ABQEyZGQCBA8PFgIfAAUY5YWs5YWx6YCJ5L+uICAgICAgICAgICAgZGQCBQ9kFgJmDxUBNTxhIGhyZWY9IyBvbmNsaWNrPSJ2aWV3VGVhY2hlcignMDAyMzU5Jyk7Ij7pmYjojJw8L2E+ZAIGD2QWBGYPFQFUPGEgY2xhc3M9J2J0biBidG4tbWluaSBidG4tcHJpbWFyeScgaHJlZj0iY2hhbmdlY2xhc3MuYXNweD9rY2g9MDAyMDA5Ij7pgInogIHluIg8L2E+ZAIBDw8WAh4PQ29tbWFuZEFyZ3VtZW50BQowMDIwMDkgICAgZGQCBw9kFgJmDxUBUjMwPGEgaHJlZj0nU2V0WHVhbmRpYW4uYXNweD9rY2g9MDAyMDA5JyBjbGFzcz0nYnRuIGJ0bi1taW5pIGJ0bi1kYW5nZXInPuiuvue9rjwvYT5kAgIPZBYQZg9kFgJmDxUBATJkAgEPDxYCHwAFCjAyNDAwNSAgICBkZAICD2QWAmYPFQFfPGEgdGl0bGU9J+afpeeci+ivvueoi+S/oeaBrycgaHJlZj0jIG9uY2xpY2s9InZpZXdDb3Vyc2UoJzAyNDAwNScpOyI+5q+V5Lia5a6e5Lmg77yINeWIhu+8iTwvYT5kAgMPDxYCHwAFATVkZAIEDw8WAh8ABRjkuJPkuJrkuLvlubIgICAgICAgICAgICBkZAIFD2QWAmYPFQE1PGEgaHJlZj0jIG9uY2xpY2s9InZpZXdUZWFjaGVyKCcwMDAwMDAnKTsiPuW+heWumjwvYT5kAgYPZBYEZg8VAVQ8YSBjbGFzcz0nYnRuIGJ0bi1taW5pIGJ0bi1wcmltYXJ5JyBocmVmPSJjaGFuZ2VjbGFzcy5hc3B4P2tjaD0wMjQwMDUiPumAieiAgeW4iDwvYT5kAgEPDxYEHwMFCjAyNDAwNSAgICAeB1Zpc2libGVoZGQCBw9kFgJmDxUBAGQCAw8PFgIfBGhkZBgBBRpjdGwwMCRjaGRDb250ZW50JGd2Q29udGVudA88KwAMAQgCAWQsDQ0NyZK40nNy0PFIwTiT8I8Z1IqEp1VkuQlB2klL8w==
            __VIEWSTATEGENERATOR: 15987359
            __EVENTVALIDATION: /wEdAAO1ZPGNtURE0LuxlpBkqiABetmnXCW78O8MOJUYt92Syd4Dpk7uptH9pM9W0hpkHiQ3LQS1zNQhyPZMKk/5v76olZM9r9JkSLIiA8BBHNnsCg==
            ctl00$chdContent$gvContent$ctl02$btnDelete: 删除课程
            '''

            self.clean_xuanke_page()
            self.get_xuanke_page()
            my_xuanke=MyXuanKe.objects.filter(student_id=self.student_id,lesson_teacher__lesson_id=kch,lesson_teacher__semester=self.next_semester)
            if my_xuanke:
                my_xuanke=my_xuanke[0]
                if my_xuanke.delete_post_code:
                    data = {
                        '__EVENTTARGET': '',
                        '__EVENTARGUMENT': '',
                        '__VIEWSTATE': hid_data[0],
                        '__VIEWSTATEGENERATOR': hid_data[1],
                        '__EVENTVALIDATION': hid_data[2],
                        my_xuanke.delete_post_code:'删除课程',
                    }
                    wb_data=self.__session.post(url=url,data=data,timeout=timeout)
                    if wb_data.status_code==requests.codes.ok:
                        print('删除" %s "成功'%my_xuanke.lesson_teacher.lesson.name)
                        self.clean_xuanke_page()
                        self.get_xuanke_page()
                        return True
                    else:
                        print('删除失败')
                        return False
                else:
                    return False
            else:
                print('删除失败，你可能没选这门课')
                return False

        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('delete_lesson timeout, retrying。。')
                return self.delete_lesson(kch=kch,limit_time=limit_ti, timeout=timeout)
            else:
                return False




if __name__ == '__main__':
    # pingjiao=Pingjiao()
    # pingjiao.login()
    xuanke=XuanKe()
    xuanke.login()
    # xuanke.set_xuandian('002913',10)
    # xuanke.delete_lesson(kch='002913',timeout=10)
    # xuanke.get_lesson_teacher('255019')
    # xuanke.get_lesson_information(kch='255019')
    # xuanke.get_all_step1_lesson_teacher_list()
    # xuanke.set_xuandian(kch='002009',xd='30')
    # xuanke.get_xuanke_page()
    # xuanke.clean_xuanke_page()
    # xuanke.get_one_step1_lesson_teacher_list(kch='056004')
    # xuanke.xuanke(kch='267269')
    # pingjiao.get_lesson()
    # pingjiao.get_my_pingjiao()
    # pingjiao.pingjiao('267211K003550BJH3|262064K004626BJH2|267155K003550BJH1|267261K003550BJH3|','056004Kt006205|267282K24982461|267212K24982461|267259K003550BJH1|')
    # pingjiao.delete_lesson('ctl00_chdContent_gvContent_ctl02_btnDelete')
    # pingjiao
    # pingjiao.get_lesson_from_lesson_subject_category()
    # pingjiao.pingjiao()

    # pingjiao.fenci()

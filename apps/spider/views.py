from django.shortcuts import render,redirect
import uuid
from django.views.generic import View,RedirectView
from celery.result import AsyncResult

# Create your views here.


from xadmin.views import CommAdminView
from .forms import GradeForm
from users.models import Colloge,Department
from semesters.models import Grade
from .tasks import get_class,get_student,get_teacher,get_department,get_colloge,get_schedule,get_score,get_new_score,get_major
from semesters.models import Semester
from .models import SpiderLog
from update.models import UpdateLog
from update.tasks import graduate_lose_efficacy,update_neo4j



class SpiderMajorView(CommAdminView):
    def get(self,request):
        context = super().get_context()  # 这一步是关键，必须super一下继承CommAdminView里面的context，不然侧栏没有对应数据，我在这里卡了好久
        title = "爬取专业"  # 定义面包屑变量
        context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})  # 把面包屑变量添加到context里面
        context["title"] = title  # 把面包屑变量添加到context里面
        spider_log = SpiderLog.objects.filter(type='Major').order_by('-start_time')[:30]
        context['spider_log'] = spider_log
        grade=Grade.objects.all()
        context['grade']=grade
        if_retry = request.GET.get('if_retry')
        if if_retry:
            if if_retry == 'true':
                id = request.GET.get('id')
                lll = SpiderLog.objects.filter(id=int(id))
                if lll:
                    lll = lll[0]
                    if lll.status == 'error':
                        lll.status = 'retried'
                        lll.save()
                    else:
                        pass
        gra = request.GET.get('grade')
        user_id = request.user.id
        if gra:
            verbose_id = uuid.uuid4()
            desc='爬取{0}级的所有专业及其培养方案'.format(gra)
            log = SpiderLog.objects.create(desc=desc, spider_class_and_method='', user_id=user_id,type='Major', verbose_id=verbose_id, status='error')
            url = r'/xadmin/spider-major/?grade={0}&if_retry=true&id={1}'.format(gra,log.id)
            log.url = url
            log.spider_class_and_method = 'SpiderStaticStudent.get_one_grade_major(log_id={0},grade_post_code="{1}")'.format(log.id,gra)
            task = get_major.apply_async((log.id,gra), retry=True,retry_policy={'max_retries': 3, 'interval_start': 0,'interval_step': 0.2, 'interval_max': 0.2, })
            # task = get_colloge.delay(log.id)
            task_id = task.id
            log.task_id = task_id
            log.save()
            context['detail'] = '后台正在爬取{0}级的所有专业及其培养方案，正在跳转到爬取日志页面……'.format(gra)
            return render(request, 'spider_major.html', context)
        else:
            return render(request,'spider_major.html',context)


class SpiderClassView(CommAdminView):
    def get(self, request):
        context = super().get_context()  # 这一步是关键，必须super一下继承CommAdminView里面的context，不然侧栏没有对应数据，我在这里卡了好久
        title = "爬取班级"  # 定义面包屑变量
        context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})  # 把面包屑变量添加到context里面
        context["title"] = title  # 把面包屑变量添加到context里面
        colloge=Colloge.objects.filter().exclude(id__in=['37000','450','81000'])
        grade=Grade.objects.all().order_by('-grade')[:5]
        context['colloge']=colloge
        context['grade']=grade
        spider_log=SpiderLog.objects.filter(type='Class').order_by('-start_time')[:30]
        context['spider_log']=spider_log
        colloge_post_code=request.GET.get('colloges')
        grade=request.GET.get('grade')
        user_id = request.user.id
        if_retry=request.GET.get('if_retry')
        if if_retry:
            if if_retry=='true':
                id=request.GET.get('id')
                lll=SpiderLog.objects.filter(id=int(id))
                if lll:
                    lll=lll[0]
                    if lll.status=='error':
                        lll.status='retried'
                        lll.save()
                    else:
                        pass
        if colloge_post_code:
            if colloge_post_code=='all':
                if grade!=None:
                    if grade=='all':
                        verbose_id=uuid.uuid4()
                        log = SpiderLog.objects.create(desc='爬取所有学院所有年级的班级', spider_class_and_method='',user_id=user_id, type='Class', verbose_id=verbose_id,status='error')
                        url = r'/xadmin/spider-class/?colloges=all&grade=all&%E5%BC%80%E5%A7%8B%E7%88%AC%E5%8F%96=%E5%BC%80%E5%A7%8B%E7%88%AC%E5%8F%96&if_retry=true&id={0}'.format(log.id)
                        log.url=url
                        task=get_class.apply_async((log.id,None,None,True,True),retry=True,retry_policy={'max_retries': 3,'interval_start': 0,'interval_step': 0.2,'interval_max': 0.2,})
                        task_id = task.id
                        log.task_id=task_id
                        log.save()
                        # post_task_id.delay(verbose_id,task_id)
                        context['detail'] = '后台正在爬取所有学院所有年级的班级，正在跳转到爬取日志页面……'
                    else:
                        verbose_id = uuid.uuid4()
                        desc = '爬取所有学院的{0}级的班级'.format(grade)
                        log = SpiderLog.objects.create(desc=desc, spider_class_and_method='', user_id=user_id,type='Class', verbose_id=verbose_id,status='error')
                        url = r'/xadmin/spider-class/?colloges=all&grade={0}&if_retry=true&id={1}'.format(grade,log.id)
                        log.url=url
                        # task = get_class.delay(log.id,None,grade,True,False)
                        # task = get_class.delay(log.id,None,grade,True,False)
                        task = get_class.apply_async((log.id,None,grade,True,False), retry=True,retry_policy={'max_retries': 3, 'interval_start': 0,'interval_step': 0.2, 'interval_max': 0.2, })
                        task_id = task.id
                        log.task_id=task_id
                        log.save()
                        context['detail'] = '后台正在爬取所有学院的{0}级的班级，正在跳转到爬取日志页面……'.format(grade)
                    return render(request, 'spider_class.html', context)
                else:
                    return render(request,'spider_class.html',context)
            else:
                colloge = Colloge.objects.filter(post_code=colloge_post_code)
                if colloge:
                    colloge = colloge[0]
                    name = colloge.name
                else:
                    context['error'] = '该学院不存在！'
                    return render(request, 'spider_class.html', context)
                if grade!=None:
                    if grade=='all':
                        verbose_id = uuid.uuid4()
                        desc = '爬取{0}的所有年级的班级'.format(name)
                        log = SpiderLog.objects.create(desc=desc, spider_class_and_method='', user_id=user_id,type='Class', verbose_id=verbose_id,status='error')
                        url = r'/xadmin/spider-class/?colloges={0}&grade=all&if_retry=true&id={1}'.format(colloge.post_code,log.id)
                        log.url=url
                        # task = get_class.delay(log.id,colloge_post_code,None,False,True)
                        task = get_class.apply_async((log.id,colloge_post_code,None,False,True), retry=True,
                                                     retry_policy={'max_retries': 3, 'interval_start': 0,
                                                                   'interval_step': 0.2, 'interval_max': 0.2, })
                        task_id = task.id
                        log.task_id=task_id
                        log.save()
                        # post_task_id.delay(verbose_id, task_id)
                        context['detail'] = '后台正在爬取{0}的所有年级的班级，正在跳转到爬取日志页面……'.format(name)
                    else:
                        verbose_id = uuid.uuid4()
                        desc = '爬取{0}的{1}级的班级'.format(name, grade)
                        log = SpiderLog.objects.create(desc=desc, spider_class_and_method='', user_id=user_id,type='Class', verbose_id=verbose_id,status='error')
                        url = r'/xadmin/spider-class/?colloges={0}&grade={1}&if_retry=true&id={2}'.format(colloge.post_code, grade,log.id)
                        log.url=url
                        # task = get_class.delay(log.id,colloge_post_code,grade,False,False)
                        task = get_class.apply_async((log.id,colloge_post_code,grade,False,False), retry=True,
                                                     retry_policy={'max_retries': 3, 'interval_start': 0,
                                                                   'interval_step': 0.2, 'interval_max': 0.2, })
                        task_id = task.id
                        log.task_id=task_id
                        log.save()
                        context['detail'] = '后台正在爬取{0}的{1}级的班级，正在跳转到爬取日志页面……'.format(name,grade)
                    return render(request, 'spider_class.html', context)
                else:
                    return render(request, 'spider_class.html', context)
        else:
            return render(request, 'spider_class.html', context)
        # 下面你可以接着写你自己的东西了，写完记得添加到context里面就可以了



class SpiderStudentView(CommAdminView):
    def get(self, request):
        context = super().get_context()  # 这一步是关键，必须super一下继承CommAdminView里面的context，不然侧栏没有对应数据，我在这里卡了好久
        title = "爬取学生"  # 定义面包屑变量
        context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})  # 把面包屑变量添加到context里面
        context["title"] = title  # 把面包屑变量添加到context里面
        colloge = Colloge.objects.filter().exclude(id__in=['37000', '450', '81000'])
        grade = Grade.objects.all().order_by('-grade')[:5]
        context['colloge'] = colloge
        context['grade'] = grade

        spider_log = SpiderLog.objects.filter(type='Student').order_by('-start_time')[:30]
        context['spider_log'] = spider_log

        colloge_post_code = request.GET.get('colloges')
        grade = request.GET.get('grade')
        user_id = request.user.id

        if_retry = request.GET.get('if_retry')
        if if_retry:
            if if_retry == 'true':
                id = request.GET.get('id')
                lll = SpiderLog.objects.filter(id=int(id))
                if lll:
                    lll = lll[0]
                    if lll.status == 'error':
                        lll.status = 'retried'
                        lll.save()
                    else:
                        pass
        if colloge_post_code:
            if colloge_post_code == 'all':
                if grade != None:
                    if grade == 'all':
                        verbose_id = uuid.uuid4()
                        log = SpiderLog.objects.create(desc='爬取所有学院所有年级的学生', spider_class_and_method='',user_id=user_id, type='Student', verbose_id=verbose_id,status='error')
                        url=r'/xadmin/spider-student/?colloges=all&grade=all&if_retry=true&id={0}'.format(log.id)
                        log.url=url
                        log.spider_class_and_method = 'SpiderStaticStudent.get_colloge_grade_student(log_id={0},colloge_post_code="all",grade="all")'.format(log.id)
                        # task = get_student.delay(log.id,'all',grade,None)
                        task = get_student.apply_async((log.id,'all',grade), retry=True,
                                                     retry_policy={'max_retries': 3, 'interval_start': 0,
                                                                   'interval_step': 0.2, 'interval_max': 0.2, })
                        task_id = task.id
                        log.task_id=task_id
                        log.save()
                        context['detail'] = '后台正在爬取所有学院所有年级的学生，正在跳转到爬取日志页面……'
                    else:
                        verbose_id = uuid.uuid4()
                        desc = '爬取所有学院所有{0}级的学生'.format(grade)
                        log = SpiderLog.objects.create(desc=desc, spider_class_and_method='', user_id=user_id,type='Student', verbose_id=verbose_id,status='error')
                        url=r'/xadmin/spider-student/?colloges=all&grade={0}&if_retry=true&id={1}'.format(grade,log.id)
                        log.url=url
                        log.spider_class_and_method = 'SpiderStaticStudent.get_colloge_grade_student(log_id={0},colloge_post_code="all",grade="{1}")'.format(log.id, grade)
                        task = get_student.apply_async((log.id,'all',grade), retry=True,
                                                     retry_policy={'max_retries': 3, 'interval_start': 0,
                                                                   'interval_step': 0.2, 'interval_max': 0.2, })

                        # task = get_student.delay(log.id,'all',grade,None)
                        task_id = task.id
                        log.task_id=task_id
                        log.save()
                        context['detail'] = '后台正在爬取所有学院的{0}级的学生，正在跳转到爬取日志页面……'.format(grade)
                    return render(request, 'spider_student.html', context)
                else:
                    return render(request, 'spider_student.html', context)
            else:
                colloge = Colloge.objects.filter(post_code=colloge_post_code)
                if colloge:
                    colloge = colloge[0]
                    name = colloge.name
                else:
                    context['error'] = '该学院不存在！'
                    return render(request, 'spider_student.html', context)
                if grade != None:
                    if grade == 'all':
                        verbose_id = uuid.uuid4()
                        desc = '爬取{0}所有年级的学生'.format(name)
                        log = SpiderLog.objects.create(desc=desc, spider_class_and_method='', user_id=user_id,type='Student', verbose_id=verbose_id,status='error')
                        url=r'/xadmin/spider-student/?colloges={0}&grade=all&if_retry=true&id={1}'.format(colloge_post_code,log.id)
                        log.url=url
                        log.spider_class_and_method = 'SpiderStaticStudent.get_colloge_grade_student(log_id={0},colloge_post_code="{1}",grade="all")'.format(log.id, colloge_post_code)
                        # task = get_student.delay(log.id,colloge_post_code,grade,name)
                        task = get_student.apply_async((log.id,colloge_post_code,grade), retry=True,retry_policy={'max_retries': 3, 'interval_start': 0,'interval_step': 0.2, 'interval_max': 0.2, })
                        task_id = task.id
                        log.task_id=task_id
                        log.save()
                        context['detail'] = '后台正在爬取{0}所有年级的学生，正在跳转到爬取日志页面……'.format(name)
                    else:
                        verbose_id = uuid.uuid4()
                        desc = '爬取{0}所有{1}级的学生'.format(name, grade)
                        log = SpiderLog.objects.create(desc=desc, spider_class_and_method='', user_id=user_id,type='Student', verbose_id=verbose_id,status='error')
                        url=r'/xadmin/spider-student/?colloges={0}&grade={1}&if_retry=true&id={2}'.format(colloge_post_code,grade,log.id)
                        log.url=url
                        log.spider_class_and_method = 'SpiderStaticStudent.get_colloge_grade_student(log_id={0},colloge_post_code="{1}",grade="{2}")'.format(log.id, colloge_post_code, grade)
                        # log.save()

                        task = get_student.apply_async((log.id,colloge_post_code,grade), retry=True,retry_policy={'max_retries': 3, 'interval_start': 0,'interval_step': 0.2, 'interval_max': 0.2, })
                        # get_student(log.id,colloge_post_code,grade)

                        task_id = task.id
                        log.task_id=task_id
                        log.save()
                        context['detail'] = '后台正在爬取{0}的{1}级的学生，正在跳转到爬取日志页面……'.format(name, grade)
                    return render(request, 'spider_student.html', context)
                else:
                    return render(request, 'spider_student.html', context)
        else:
            return render(request, 'spider_student.html', context)
        # 下面你可以接着写你自己的东西了，写完记得添加到context里面就可以了


class SpiderTeacherView(CommAdminView):
    def get(self,request):
        context = super().get_context()  # 这一步是关键，必须super一下继承CommAdminView里面的context，不然侧栏没有对应数据，我在这里卡了好久
        title = "爬取教师"  # 定义面包屑变量
        context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})  # 把面包屑变量添加到context里面
        context["title"] = title  # 把面包屑变量添加到context里面
        department=Department.objects.all()
        context['department']=department
        spider_log = SpiderLog.objects.filter(type='Teacher').order_by('-start_time')[:30]
        context['spider_log'] = spider_log
        department_post_code = request.GET.get('departments')
        user_id = request.user.id
        if_retry = request.GET.get('if_retry')
        if if_retry:
            if if_retry == 'true':
                id = request.GET.get('id')
                lll = SpiderLog.objects.filter(id=int(id))
                if lll:
                    lll = lll[0]
                    if lll.status == 'error':
                        lll.status = 'retried'
                        lll.save()
                    else:
                        pass
        if department_post_code:
            if department_post_code=='all':
                verbose_id = uuid.uuid4()
                log = SpiderLog.objects.create(desc='爬取所有部门的教工', spider_class_and_method='', user_id=user_id,type='Teacher', verbose_id=verbose_id,status='error')
                log.spider_class_and_method = 'SpiderStaticTeacher.get_teacher(log_id={0})'.format(log.id)
                # task = get_teacher.delay(log.id,'all')
                url=r'/xadmin/spider-teacher/?departments=all&if_retry=true&id={0}'.format(log.id)
                log.url=url
                task = get_teacher.apply_async((log.id,'all'), retry=True,retry_policy={'max_retries': 3, 'interval_start': 0, 'interval_step': 0.2,'interval_max': 0.2, })
                task_id = task.id
                log.task_id=task_id
                log.save()
                context['detail']='后台正在爬取所有部门的教师，正在跳转到爬取日志页面……'
            else:
                dep=Department.objects.filter(post_code=department_post_code)
                if dep:
                    dep=dep[0]
                    verbose_id = uuid.uuid4()
                    desc = '爬取{0}部门的教工'.format(dep.name)
                    log = SpiderLog.objects.create(desc=desc, spider_class_and_method='', user_id=user_id,type='Teacher', verbose_id=verbose_id,status='error')
                    url=r'/xadmin/spider-teacher/?departments={0}&if_retry=true&id={1}'.format(department_post_code,log.id)
                    log.url=url
                    log.spider_class_and_method = 'SpiderStaticTeacher.get_one_colloge_teachers(post_code="{0}",log_id={1})'.format(department_post_code, log.id)
                    task = get_teacher.apply_async((log.id,department_post_code), retry=True,retry_policy={'max_retries': 3, 'interval_start': 0,'interval_step': 0.2, 'interval_max': 0.2, })
                    # task = get_teacher.delay(log.id,department_post_code)
                    task_id = task.id
                    log.task_id=task_id
                    log.save()
                    context['detail'] = '后台正在爬取{0}部门的教师，正在跳转到爬取日志页面……'.format(dep.name)
                else:
                    context['error']='部门不存在！'
            return render(request,'spider_teacher.html',context)
        else:
            return render(request,'spider_teacher.html',context)

class SpiderDepartmentView(CommAdminView):
    def get(self,request):
        context = super().get_context()  # 这一步是关键，必须super一下继承CommAdminView里面的context，不然侧栏没有对应数据，我在这里卡了好久
        title = "爬取教师部门"  # 定义面包屑变量
        context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})  # 把面包屑变量添加到context里面
        context["title"] = title  # 把面包屑变量添加到context里面
        spider_log = SpiderLog.objects.filter(type='Department').order_by('-start_time')[:30]
        context['spider_log'] = spider_log
        if_retry = request.GET.get('if_retry')
        if if_retry:
            if if_retry == 'true':
                id = request.GET.get('id')
                lll = SpiderLog.objects.filter(id=int(id))
                if lll:
                    lll = lll[0]
                    if lll.status == 'error':
                        lll.status = 'retried'
                        lll.save()
                    else:
                        pass
        all_department = request.GET.get('all-department')
        user_id = request.user.id
        if all_department:
            if all_department=='all':
                verbose_id = uuid.uuid4()
                log = SpiderLog.objects.create(desc='爬取所有教工部门', spider_class_and_method='', user_id=user_id,type='Department', verbose_id=verbose_id,status='error')
                log.spider_class_and_method = 'SpiderStaticTeacher.get_department(log_id={0})'.format(log.id)
                url=r'/xadmin/spider-department/?all-department=all&if_retry=true&id={0}'.format(log.id)
                log.url=url
                task = get_department.apply_async((log.id,), retry=True,
                                               retry_policy={'max_retries': 3, 'interval_start': 0,
                                                             'interval_step': 0.2, 'interval_max': 0.2, })
                # task = get_department.delay(log.id)
                task_id = task.id
                log.task_id=task_id
                log.save()
                context['detail']='后台正在爬取教工部门，正在跳转到爬取日志页面……'
                return render(request, 'spider_department.html', context)
            else:
                return render(request, 'spider_department.html', context)
        else:
            return render(request, 'spider_department.html', context)

class SpiderCollogeView(CommAdminView):
    def get(self,request):
        context = super().get_context()  # 这一步是关键，必须super一下继承CommAdminView里面的context，不然侧栏没有对应数据，我在这里卡了好久
        title = "爬取学院"  # 定义面包屑变量
        context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})  # 把面包屑变量添加到context里面
        context["title"] = title  # 把面包屑变量添加到context里面
        spider_log = SpiderLog.objects.filter(type='Colloge').order_by('-start_time')[:30]
        context['spider_log'] = spider_log
        if_retry = request.GET.get('if_retry')
        if if_retry:
            if if_retry == 'true':
                id = request.GET.get('id')
                lll = SpiderLog.objects.filter(id=int(id))
                if lll:
                    lll = lll[0]
                    if lll.status == 'error':
                        lll.status = 'retried'
                        lll.save()
                    else:
                        pass
        all_colloge = request.GET.get('all-colloge')
        user_id = request.user.id
        if all_colloge:
            if all_colloge=='all':
                verbose_id = uuid.uuid4()
                log = SpiderLog.objects.create(desc='爬取所有学院', spider_class_and_method='', user_id=user_id,type='Colloge', verbose_id=verbose_id,status='error')
                url = r'/xadmin/spider-colloge/?all-colloge=all&if_retry=true&id={0}'.format(log.id)
                log.url = url
                log.spider_class_and_method = 'SpiderStaticStudent.get_colloges(log_id={0})'.format(log.id)
                task = get_colloge.apply_async((log.id,), retry=True,
                                               retry_policy={'max_retries': 3, 'interval_start': 0,
                                                             'interval_step': 0.2, 'interval_max': 0.2, })
                # task = get_colloge.delay(log.id)
                task_id = task.id
                log.task_id=task_id
                log.save()
                context['detail'] = '后台正在爬取所有学院，正在跳转到爬取日志页面……'
                return render(request, 'spider_colloge.html', context)
            else:
                return render(request,'spider_colloge.html',context)
        else:
            return render(request,'spider_colloge.html',context)


class SpiderScheduleView(CommAdminView):
    def get(self,request):
        context = super().get_context()  # 这一步是关键，必须super一下继承CommAdminView里面的context，不然侧栏没有对应数据，我在这里卡了好久
        title = "爬取教师和学生课表及名单"  # 定义面包屑变量
        context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})  # 把面包屑变量添加到context里面
        context["title"] = title  # 把面包屑变量添加到context里面
        semester=Semester.objects.all().order_by('post_code')
        context['semester']=semester
        spider_log = SpiderLog.objects.filter(type='Schedule').order_by('-start_time')[:30]
        context['spider_log'] = spider_log
        if_retry = request.GET.get('if_retry')
        if if_retry:
            if if_retry == 'true':
                id = request.GET.get('id')
                lll = SpiderLog.objects.filter(id=int(id))
                if lll:
                    lll = lll[0]
                    if lll.status == 'error':
                        lll.status = 'retried'
                        lll.save()
                    else:
                        pass
        semes=request.GET.get('semester')
        user_id = request.user.id
        if semes:
            if semes=='all':
                verbose_id = uuid.uuid4()
                log = SpiderLog.objects.create(desc='爬取所有教师和学生所有学期的课表', spider_class_and_method='', user_id=user_id,type='Schedule', verbose_id=verbose_id,status='error')
                log.spider_class_and_method = 'SpiderStaticTeacher.get_schedule(log_id={0})'.format(log.id)
                url=r'/xadmin/spider-schedule/?semester=all&if_retry=true&id={0}'.format(log.id)
                log.url=url
                task = get_schedule.apply_async((log.id,'all'), retry=True,
                                               retry_policy={'max_retries': 3, 'interval_start': 0,
                                                             'interval_step': 0.2, 'interval_max': 0.2, })
                # task = get_schedule.delay(log.id,'all')
                task_id = task.id
                log.task_id=task_id
                log.save()
                context['detail']='后台正在爬取所有学期的所有教师和学生的课表，正在跳转到爬取日志页面……'
            else:
                se=Semester.objects.filter(post_code=semes)
                if se:
                    se=se[0]
                    verbose_id = uuid.uuid4()
                    desc = '爬取所有教师和学生{0}的课表'.format(se.verbose_name)
                    log = SpiderLog.objects.create(desc=desc, spider_class_and_method='', user_id=user_id,type='Schedule', verbose_id=verbose_id,status='error')
                    url = r'/xadmin/spider-schedule/?semester={0}&if_retry=true&id={1}'.format(semes,log.id)
                    log.url = url
                    log.spider_class_and_method = 'SpiderStaticTeacher.get_one_semester_schedule(semester="{0}",log_id={1})'.format(semester, log.id)
                    task = get_schedule.apply_async((log.id,se.post_code), retry=True,
                                                   retry_policy={'max_retries': 3, 'interval_start': 0,
                                                                 'interval_step': 0.2, 'interval_max': 0.2, })
                    # task = get_schedule.delay(log.id,se.post_code)
                    task_id = task.id
                    log.task_id=task_id
                    log.save()
                    context['detail'] = '后台正在爬取{0}的所有教师和学生的课表，正在跳转到爬取日志页面……'.format(se.verbose_name)
                else:
                    context['error']='学期不存在！'
            return render(request,'spider_schedule.html',context)
        else:
            return render(request,'spider_schedule.html',context)

class SpiderScoreView(CommAdminView):
    def get(self,request):
        context = super().get_context()  # 这一步是关键，必须super一下继承CommAdminView里面的context，不然侧栏没有对应数据，我在这里卡了好久
        title = "爬取成绩"  # 定义面包屑变量
        context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})  # 把面包屑变量添加到context里面
        context["title"] = title  # 把面包屑变量添加到context里面
        semester=Semester.objects.all().order_by('post_code')
        context['semester']=semester
        spider_log = SpiderLog.objects.filter(type='Score').order_by('-start_time')[:30]
        context['spider_log'] = spider_log
        if_retry = request.GET.get('if_retry')
        if if_retry:
            if if_retry == 'true':
                id = request.GET.get('id')
                lll = SpiderLog.objects.filter(id=int(id))
                if lll:
                    lll = lll[0]
                    if lll.status == 'error':
                        lll.status = 'retried'
                        lll.save()
                    else:
                        pass
        all_student=request.GET.get('all_student')
        user_id = request.user.id
        if all_student:
            if all_student=='all':
                verbose_id = uuid.uuid4()
                log = SpiderLog.objects.create(desc='爬取所有注册过的学生的成绩', spider_class_and_method='', user_id=user_id,type='Score', verbose_id=verbose_id,status='error')
                url = r'/xadmin/spider-score/?all_student=all&if_retry=true&id={0}'.format(log.id)
                log.url = url
                log.spider_class_and_method = 'SpiderDynamicStudent.get_my_studyData()'
                task = get_score.apply_async((log.id,), retry=True,
                                               retry_policy={'max_retries': 3, 'interval_start': 0,
                                                             'interval_step': 0.2, 'interval_max': 0.2, })
                # task = get_score.delay(log.id)
                task_id = task.id
                log.task_id=task_id
                log.save()
                context['detail']='后台正在爬取所有已注册的学生的成绩，正在跳转到爬取日志页面……'
                return render(request, 'spider_score.html', context)
            else:
                return render(request, 'spider_score.html', context)
        else:
            return render(request,'spider_score.html',context)


class SpiderNewScoreView(CommAdminView):
    def get(self,request):
        context = super().get_context()  # 这一步是关键，必须super一下继承CommAdminView里面的context，不然侧栏没有对应数据，我在这里卡了好久
        title = "爬取学院"  # 定义面包屑变量
        context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})  # 把面包屑变量添加到context里面
        context["title"] = title  # 把面包屑变量添加到context里面
        semester=Semester.objects.all().order_by('post_code')
        context['semester']=semester
        spider_log = SpiderLog.objects.filter(type='NewScore').order_by('-start_time')[:30]
        context['spider_log'] = spider_log
        if_retry = request.GET.get('if_retry')
        if if_retry:
            if if_retry == 'true':
                id = request.GET.get('id')
                lll = SpiderLog.objects.filter(id=int(id))
                if lll:
                    lll = lll[0]
                    if lll.status == 'error':
                        lll.status = 'retried'
                        lll.save()
                    else:
                        pass
        all_student=request.GET.get('all_student')
        user_id = request.user.id
        if all_student:
            if all_student=='all':
                verbose_id = uuid.uuid4()
                log = SpiderLog.objects.create(desc='爬取所有注册过的学生的最新成绩', spider_class_and_method='', user_id=user_id,type='NewScore', verbose_id=verbose_id,status='error')
                url = r'/xadmin/spider-new-score/?all_student=all&if_retry=true&id={0}'.format(log.id)
                log.url = url
                log.spider_class_and_method = 'SpiderDynamicStudent.get_new_score()'
                task = get_new_score.apply_async((log.id,), retry=True,
                                               retry_policy={'max_retries': 3, 'interval_start': 0,
                                                             'interval_step': 0.2, 'interval_max': 0.2, })
                # task = get_score.delay(log.id)
                task_id = task.id
                log.task_id=task_id
                log.save()
                context['detail']='后台正在爬取所有已注册的学生的最新成绩，正在跳转到爬取日志页面……'
                return render(request, 'spider_new_score.html', context)
            else:
                return render(request, 'spider_new_score.html', context)
        else:
            return render(request,'spider_new_score.html',context)


class StopTaskView(View):
    def get(self,request):
        id=request.GET.get('id')
        url=request.GET.get('url')
        if id:
            log=SpiderLog.objects.filter(id=id)
            if log:
                log=log[0]
                try:
                    AsyncResult(id=log.task_id).revoke(terminate=True)
                except:
                    pass
                log.status='stopped'
                log.save()
                if url:
                    return redirect(url)
                else:
                    return redirect('/xadmin/spider-colloge/')
            else:
                if url:
                    return redirect(url)
                else:
                    return redirect('/xadmin/spider-colloge/')
        else:
            if url:
                return redirect(url)
            else:
                return redirect('/xadmin/spider-colloge/')


class GraduateLoseEfficacyView(CommAdminView):
    def get(self,request):
        context = super().get_context()  # 这一步是关键，必须super一下继承CommAdminView里面的context，不然侧栏没有对应数据，我在这里卡了好久
        title = "毕业生失效"  # 定义面包屑变量
        context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})  # 把面包屑变量添加到context里面
        context["title"] = title  # 把面包屑变量添加到context里面
        grade = Grade.objects.all().order_by('-grade')
        context['grade']=grade
        update_log = UpdateLog.objects.filter(type='Graduate').order_by('-start_time')[:30]
        context['update_log'] = update_log
        if_retry = request.GET.get('if_retry')
        if if_retry:
            if if_retry == 'true':
                id = request.GET.get('id')
                lll = SpiderLog.objects.filter(id=int(id))
                if lll:
                    lll = lll[0]
                    if lll.status == 'error':
                        lll.status = 'retried'
                        lll.save()
                    else:
                        pass
        gra=request.GET.get('grade')
        user_id=request.user.id
        if gra:
            try:
                gra=int(gra)
                verbose_id = uuid.uuid4()
                desc = '使{0}年级的毕业生失效'.format(gra)
                log = UpdateLog.objects.create(desc=desc, class_and_method='', user_id=user_id, type='Graduate',verbose_id=verbose_id, status='error')
                url = r'/xadmin/graduate-lose-efficacy/?grade={0}&if_retry=true&id={1}'.format(gra,log.id)
                log.url = url
                task = graduate_lose_efficacy.apply_async((log.id, gra), retry=True,retry_policy={'max_retries': 3, 'interval_start': 0,'interval_step': 0.2, 'interval_max': 0.2, })
                task_id = task.id
                log.task_id = task_id
                log.save()
                context['detail']='正在后台更新'
            except:
                context['error']='未找到该年级！'
        return render(request,'graduate_lose_efficacy.html',context)


class Neo4jView(CommAdminView):
    def get(self,request):
        context = super().get_context()  # 这一步是关键，必须super一下继承CommAdminView里面的context，不然侧栏没有对应数据，我在这里卡了好久
        title = "更新图数据库"  # 定义面包屑变量
        context["breadcrumbs"].append({'url': '/cwyadmin/', 'title': title})  # 把面包屑变量添加到context里面
        context["title"] = title  # 把面包屑变量添加到context里面
        update_log = UpdateLog.objects.filter(type='Neo4j').order_by('-start_time')[:30]
        context['update_log'] = update_log
        semester=Semester.objects.all().order_by('-post_code')
        context['semester']=semester
        if_retry = request.GET.get('if_retry')
        if if_retry:
            if if_retry == 'true':
                id = request.GET.get('id')
                lll = SpiderLog.objects.filter(id=int(id))
                if lll:
                    lll = lll[0]
                    if lll.status == 'error':
                        lll.status = 'retried'
                        lll.save()
                    else:
                        pass
        # update=request.GET.get('update')
        user_id=request.user.id
        seme=request.GET.get('semester')
        if seme:
            verbose_id = uuid.uuid4()
            desc = '更新了图数据库'
            log = UpdateLog.objects.create(desc=desc, class_and_method='', user_id=user_id, type='Neo4j',verbose_id=verbose_id, status='error')
            url = r'/xadmin/neo4j/?update=update&if_retry=true&id={0}'.format(log.id)
            log.url = url
            task = update_neo4j.apply_async((log.id,seme), retry=True,retry_policy={'max_retries': 3, 'interval_start': 0,'interval_step': 0.2, 'interval_max': 0.2, })
            task_id = task.id
            log.task_id = task_id
            log.save()
            context['detail']='正在后台更新'
        return render(request,'neo4j.html',context)

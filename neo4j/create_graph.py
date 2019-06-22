#-*- coding:utf-8 -*-
from py2neo import Graph,Database,NodeMatcher,RelationshipMatcher
from py2neo.data import Node,Relationship


# import os,django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
# django.setup()

from users.models import Student,Teacher,Department,Class,Major
from semesters.models import Semester
from lessons.models import ScheduleLesson,Lesson,MajorLesson
from scores.models import Score

from jwxzs_2.settings import NEO4J_HOST,NEO4J_USERNAME,NEO4J_PASSWORD

# import pymongo
import jieba


from subject.models import LessonLabels


class JwxzsGraph(object):
    def __init__(self):
        self.graph = Graph(NEO4J_HOST,auth=(NEO4J_USERNAME,NEO4J_PASSWORD))
        # self.graph.name='JwxzsGraph'
        self.matcher=NodeMatcher(self.graph)
        self.rela_matcher=RelationshipMatcher(self.graph)
        self.graph.run('CREATE CONSTRAINT ON (p:Teacher) ASSERT p.id IS UNIQUE')
        self.graph.run('CREATE CONSTRAINT ON (p:Student) ASSERT p.id IS UNIQUE')
        self.graph.run('CREATE CONSTRAINT ON (p:Lesson) ASSERT p.id IS UNIQUE')
        self.graph.run('CREATE CONSTRAINT ON ()-[a:开设]->() ASSERT exists(a.semester)')
        self.graph.run('CREATE CONSTRAINT ON ()-[a:学习]->() ASSERT exists(a.semester)')
        self.graph.run('CREATE CONSTRAINT ON ()-[a:师生]->() ASSERT exists(a.semester)')
        # self.client = pymongo.MongoClient(host='localhost', port=27017, connect=False)
        # self.subject_system = self.client['subject_system']
        # self.subject_system.authenticate(name='subject_system_user', password='ssum2567076458')
        # self.sebject_system_lesson = self.subject_system['sebject_system_lesson']

        # for i in sebject_system_lesson.find():
        # self.graph.run('CREATE CONSTRAINT ON (p:Department) ASSERT p.id IS UNIQUE')


    # def create_teacher_node(self):
    #     lesson_node = Node('Lesson', name='算法与数据结构')
    #     self.graph.create(lesson_node)
    #     print(lesson_node)

    # def create_department_node(self):
    #     deps=Department.objects.all()
    #     for dep in deps:
    #         dep_node=Node('Group','Department',id=dep.id,name=dep.name)


    def find_lesson_tags(self,id):
        # a=self.sebject_system_lesson.find_one({'uk_lesson_id':id})
        lesson_labels=LessonLabels.objects.filter(lesson_id=id).values('label').distinct()
        a=[lab['label'] for lab in lesson_labels]
        if a:
            return a
        else:
            return None
        # print(a['tags'])
        # return a

    def create_lesson_node(self):
        lessons=Lesson.objects.all()
        for less in lessons:
            lesson_node=self.matcher.match('Lesson',id=less.id)
            if not lesson_node:
                lesson_node=Node('Lesson',id=less.id,name=less.name,credit=less.credit,if_public=less.if_public_elective,before_learning_text=less.before_learning_text,profile=less.profile,admin_department=less.admin_department,open_semester=less.open_semester)
                tags=self.find_lesson_tags(less.id)
                if tags:
                    for tag in tags:
                        tag=tag.strip()
                        try:
                            int(tag)
                        except:
                            lesson_node.add_label(tag)
                else:
                    tags=jieba.cut(less.name,cut_all=True)
                    for tag in tags:
                        tag=tag.strip()
                        if tag:
                            try:
                                int(tag)
                            except:
                                if len(tag)>1 and tag[0]!='u':
                                    print(tag)
                                    lesson_node.add_label(tag)
                        else:
                            # print(tag)
                            pass
                self.graph.create(lesson_node)
            else:
                print('Node exist!')
            # print(lesson_node)


    def create_all_student_node(self):
        students=Student.objects.filter(is_active=True)
        for stu in students:
            stu_nodes=self.matcher.match('Student',id=stu.id)
            if stu_nodes:
                print('Student node exist!')
            else:
                gender='女' if stu.gender=='female' else '男'
                if stu.image:
                    src = 'http://127.0.0.1:8000/media/' + str(stu.image)
                else:
                    src = None
                stu_node=Node('Person','Student',id=stu.id,name=stu.name,gender=gender,cla=stu.cla.name,grade=stu.cla.grade,colloge=stu.cla.colloge.name,image=src)
                self.graph.create(stu_node)
                print(stu_node)


    def create_all_teacher_node(self):
        teachers=Teacher.objects.all()
        for tea in teachers:
            tea_nodes=self.matcher.match('Teacher',id=tea.id)
            if tea_nodes:
                print('Teacher node exist!')
            else:
                gender = '女' if tea.gender == 'female' else '男'
                if tea.image:
                    src = 'http://127.0.0.1:8000/media/' + str(tea.image)
                else:
                    src = None
                tea_node = Node('Person', 'Teacher', id=tea.id,name=tea.name, gender=gender,departmen=tea.department.name,image=src)
                self.graph.create(tea_node)
                print(tea_node)


    def select_schedule_lesson(self,semester):
        sch_less=ScheduleLesson.objects.filter(semester=semester)
        for s_l in  sch_less:
            semester = Semester.objects.filter(post_code=s_l.semester)[0].verbose_name
            lesson_node = self.matcher.match('Lesson', id=s_l.lesson_id).first()
            tea=s_l.teacher
            students = s_l.score_set.values('student').distinct()
            if tea:
                tea_node=self.matcher.match('Teacher',id=tea.id).first()
                self.create_tea_less_rela(tea_id=tea.id,less_id=s_l.lesson_id,tea_node=tea_node,less_node=lesson_node,semester=semester,class_name=s_l.class_name)
                for stu in students:
                    student=Student.objects.get(id=stu['student'])
                    stu_node=self.matcher.match('Student',id=student.id).first()
                    self.create_tea_stu_rela(tea_id=tea.id,stu_id=student.id,tea_node=tea_node, stu_node=stu_node, semester=semester,class_name=s_l.class_name, lesson_name=s_l.lesson.name)
                    self.create_stu_less_rela(stu_id=student.id,less_id=s_l.lesson_id,stu_node=stu_node, less_node=lesson_node, semester=semester,class_name=s_l.class_name,teacher_name=s_l.teacher.name)
            else:
                for stu in students:
                    student = Student.objects.get(id=stu['student'])
                    stu_node = self.matcher.match('Student', id=student.id).first()
                    self.create_stu_less_rela(stu_id=student.id,less_id=s_l.lesson_id,stu_node=stu_node, less_node=lesson_node, semester=semester)



    def create_tea_stu_rela(self,tea_node,stu_node,tea_id,stu_id,semester,class_name,lesson_name):
        rela = self.rela_matcher.match([tea_node, stu_node], r_type='师生', semester=semester,lesson_name=lesson_name)
        if not rela:
            cypher='''MATCH (a:Teacher),(b:Student) WHERE a.id = "%s" AND b.id = "%s" CREATE (a)-[r:师生 {semester:"%s",class_name:"%s",lesson_name:"%s"}]->(b) RETURN r''' % (tea_id,stu_id,semester,class_name,lesson_name)
            rela=self.graph.run(cypher)
            print(rela.data())
        else:
            print('Relationship exist!')


    def create_stu_less_rela(self,stu_id,less_id,stu_node,less_node,semester,class_name=None,teacher_name=None):
        rela = self.rela_matcher.match([stu_node,less_node], r_type='学习', semester=semester)
        if not rela:
            # rela = Relationship(stu_node, '学习', less_node, semester=semester,class_name=class_name,teacher_name=teacher_name)
            if teacher_name!=None:
                cypher='''MATCH (a:Student),(b:Lesson) WHERE a.id="%s" AND b.id="%s" CREATE (a)-[r:学习 {semester:"%s",class_name:"%s",teacher_name:"%s"}]->(b) RETURN r'''%(stu_id,less_id,semester,class_name,teacher_name)
            else:
                cypher='''MATCH (a:Student),(b:Lesson) WHERE a.id="%s" AND b.id="%s" CREATE (a)-[r:学习 {semester:"%s"}]->(b) RETURN r''' % (stu_id,less_id,semester)
            rela=self.graph.run(cypher)
            print(rela.data())
        else:
            print('Relationship exist!')


    def create_tea_less_rela(self,tea_id,less_id,tea_node,less_node,semester,class_name):
        rela = self.rela_matcher.match([tea_node, less_node], r_type='开设', semester=semester,class_name=class_name)
        if not rela:
            # rela = Relationship(tea_node, '开设', less_node, semester=semester, class_name=class_name)
            # print(semester)
            cypher='''MATCH (a:Teacher),(b:Lesson) WHERE a.id="%s" AND b.id="%s" CREATE (a)-[r:开设 {semester:"%s",class_name:"%s"}]->(b) RETURN r''' % (tea_id,less_id,semester,class_name)
            # print(cypher)
            rela=self.graph.run(cypher)
            print(rela.data())
        else:
            print('Relationship exist!')


    # def create_classmate_relation(self):
    #     classes=Class.objects.all()
    #     for cla in classes:
    #         stu_ids=cla.student_set.values('id').distinct()
    #         for id_1 in stu_ids:
    #             # print(id_1)
    #             id1=id_1['id']
    #             node1=self.matcher.match('Student',id=id1).first()
    #             for id_2 in stu_ids:
    #                 id2=id_2['id']
    #                 node2=self.matcher.match('Student',id=id2).first()
    #                 if id1!=id2:
    #                     # rela_cypher=''' MATCH (a:Student{id:"%s"})-[r:同班同学 {class_name:"%s"}] -> (b:Student{id:"%s"}) RETURN r'''%(id1,cla.name,id2)
    #                     # rela=self.graph.run(rela_cypher)
    #                     rela=self.rela_matcher.match([node1,node2],r_type='同班同学',class_name=cla.name)
    #                     if not rela:
    #                         cypher='''MATCH (a:Student),(b:Student) WHERE a.id="%s" AND b.id="%s" CREATE (a)-[r:同班同学 {class_name:"%s"} ]->(b) RETURN r''' % (id1,id2,cla.name)
    #                         rela=self.graph.run(cypher)
    #                         print(rela)
    #                     else:
    #                         print('Classmate relationship exist!','  ',rela)


    def test3(self):
        s_ls=ScheduleLesson.objects.filter(class_name__startswith='|')
        for s_l in s_ls:
            semester = Semester.objects.filter(post_code=s_l.semester)[0].verbose_name
            lesson_node = self.matcher.match('Lesson', id=s_l.lesson_id).first()
            tea = s_l.teacher
            students = s_l.score_set.values('student').distinct()
            if tea:
                tea_node = self.matcher.match('Teacher', id=tea.id).first()
                self.create_tea_less_rela(tea_id=tea.id, less_id=s_l.lesson_id, tea_node=tea_node,less_node=lesson_node, semester=semester, class_name=s_l.class_name)
                for stu in students:
                    student = Student.objects.get(id=stu['student'])
                    stu_node = self.matcher.match('Student', id=student.id).first()
                    self.create_tea_stu_rela(tea_id=tea.id, stu_id=student.id, tea_node=tea_node, stu_node=stu_node,semester=semester, class_name=s_l.class_name, lesson_name=s_l.lesson.name)
                    self.create_stu_less_rela(stu_id=student.id, less_id=s_l.lesson_id, stu_node=stu_node,less_node=lesson_node, semester=semester, class_name=s_l.class_name,teacher_name=s_l.teacher.name)
            else:
                for stu in students:
                    student = Student.objects.get(id=stu['student'])
                    stu_node = self.matcher.match('Student', id=student.id).first()
                    self.create_stu_less_rela(stu_id=student.id, less_id=s_l.lesson_id, stu_node=stu_node,less_node=lesson_node, semester=semester)



    def test(self):
        node=Node('Teacher',id=1,name='jack')
        self.graph.create(node)
        node = Node('Teacher', id=1, name='bob')
        self.graph.create(node)

    def test2(self,id):
        lesson_node = self.matcher.match('Lesson', id=id)
        print(lesson_node)
        print(lesson_node.first())



    def test5(self,semester):
        node1=self.matcher.match('Teacher',id='003550').first()
        node2=self.matcher.match('Lesson',id='267092').first()
        class_name='拆班王渊#2班'
        rela=self.rela_matcher.match([node1,node2],r_type='OPEN',semester=semester,class_name=class_name)
        if not rela:
            rela=Relationship(node1,'OPEN',node2,semester=semester,class_name=class_name)
            self.graph.create(rela)
            print(rela)

    def test4(self):
        node1 = Node('Person', 'Teacher', id='003550', name='王渊')
        self.graph.create(node1)
        print(node1)

    def delete_all(self):
        self.graph.delete_all()

    #创建专业节点并创建专业课联系
    def create_major_node(self):
        majors=Major.objects.filter(is_active=True)
        for maj in majors:
            ma=self.matcher.match('Major',id=maj.major_id,grade=maj.grade)
            if not ma:
                maj_node=Node('Major',id=maj.major_id,name=maj.name,grade=maj.grade,minimum_graduation_credit=maj.minimum_graduation_credit,degree=maj.degree,subject=maj.subject)
                self.graph.create(maj_node)
                print('专业创建成功')
                self.create_maj_less_rela(maj=maj,maj_node=maj_node)
            else:
                print('major node exist! ')

    #创建专业课程联系
    def create_maj_less_rela(self,maj,maj_node):
        major_less=MajorLesson.objects.filter(major=maj)
        if major_less:
            for maj_less in major_less:
                lesson=maj_less.lesson
                less_nodes=self.matcher.match('Lesson',id=lesson.id)
                if less_nodes:
                    less_node=less_nodes.first()
                    maj_less_rela=self.rela_matcher.match([maj_node,less_node],r_type='培养方案')
                    if not maj_less_rela:
                        if_degree='true' if maj_less.if_degree else 'false'
                        # if maj_less.lesson_type==1:
                        #     ty='公共必修'
                        # elif maj_less.lesson_type==2:
                        #     ty=''
                        cypher=''' MATCH (a:Major {id:"%s",grade:%d}),(b:Lesson {id:"%s"}) CREATE (a)-[r:培养方案 {type:"%s",if_degree:%s}]->(b) RETURN r'''%(maj.major_id,maj.grade,lesson.id,maj_less.get_lesson_type_display(),if_degree)
                        rela=self.graph.run(cypher)
                        print(rela.data())
                    else:
                        print('major lesson relation exist!')
        else:
            print('the major has no major lesson!')


    #创建学生专业关系
    def create_stu_maj_rela(self):
        students=Student.objects.all()
        for stu in students:
            if stu.cla.name=='退学':
                pass
            else:
                if stu.cla.major:
                    cypher=''' MATCH (a:Student),(b:Major) WHERE a.id="%s" AND b.id="%s" AND b.grade=%d CREATE (a)-[r:专业]->(b) RETURN r'''%(stu.id,stu.cla.major.major_id,stu.cla.grade)
                    rela=self.graph.run(cypher=cypher)
                    print(rela.data())
                else:
                    print('该学生专业未知！')

    #创建相似专业关系
    def create_like_maj_rela(self):
        majors=Major.objects.all()
        for maj in majors:
            ma = self.matcher.match('Major', id=maj.major_id, grade=maj.grade)
            if ma:
                if maj.similar_major:
                    simi_maj_list=maj.similar_major.split('、')
                    if simi_maj_list:
                        for simi_maj in simi_maj_list:
                            another_majors=Major.objects.filter(name__icontains=simi_maj.strip(),grade=maj.grade)
                            if another_majors:
                                for ano_maj in another_majors:
                                    if ano_maj.major_id == maj.major_id and ano_maj.grade == maj.grade:
                                        print('专业不能和自己相似！')
                                    else:
                                        ana_maj_node=self.matcher.match('Major',id=ano_maj.major_id,grade=ano_maj.grade).first()
                                        r_l=self.rela_matcher.match([ma.first(),ana_maj_node],r_type='相似专业')
                                        if not r_l:
                                            cypher = ''' MATCH (a:Major),(b:Major) WHERE a.id="%s" AND a.grade=%d AND b.id="%s" AND b.grade=%d CREATE (a)-[r:相似专业]->(b) RETURN r''' % (
                                            maj.major_id, maj.grade, ano_maj.major_id, ano_maj.grade)
                                            rela = self.graph.run(cypher)
                                            print(rela.data())
                                        else:
                                            print('该相似专业关系已建立！')
                            else:
                                print('未查找到到该相似专业！')
                    else:
                        simi_maj=maj.similar_major.strip()
                        another_majors = Major.objects.filter(name__icontains=simi_maj,grade=maj.grade)
                        if another_majors:
                            for ano_maj in another_majors:
                                if ano_maj.major_id==maj.major_id and ano_maj.grade==maj.grade:
                                    print('专业不能和自己相似！')
                                else:
                                    ana_maj_node = self.matcher.match('Major',id=ano_maj.major_id,grade=ano_maj.grade).first()
                                    r_l = self.rela_matcher.match([ma.first(), ana_maj_node], r_type='相似专业')
                                    if not r_l:
                                        cypher=''' MATCH (a:Major),(b:Major) WHERE a.id="%s" AND a.grade=%d AND b.id="%s" AND b.grade=%d CREATE (a)-[r:相似专业]->(b) RETURN r''' % (maj.major_id,maj.grade,ano_maj.major_id,ano_maj.grade)
                                        rela=self.graph.run(cypher)
                                        print(rela.data())
                                    else:
                                        print('该相似专业关系已建立！')
                        else:
                            print('未找到该相似专业！')

    def update_lesson_node(self):
        lessons=Lesson.objects.all()
        for les in lessons:
            less_nodes=self.matcher.match('Lesson',id=les.id)
            if less_nodes:
                less_node=less_nodes.first()
                less_node['before_learning_text']=les.before_learning_text if les.before_learning_text else None
                less_node['profile']=les.profile if les.profile else None
                less_node['admin_department']=les.admin_department.name if les.admin_department else None
                less_node['open_semester']=les.open_semester if les.open_semester else None
                self.graph.push(less_node)
                print(less_node)
                # less_node.

    def update_student_image(self):
        students=Student.objects.all()
        for stu in students:
            stu_node=self.matcher.match('Student',id=stu.id).first()
            if stu.image:
                src='http://127.0.0.1:8000/media/' + str(stu.image)
            else:
                src=None
            stu_node['image']=src

            self.graph.push(stu_node)
            print(stu_node)

    def update_teacher_image(self):
        teachers = Teacher.objects.all()
        for tea in teachers:
            tea_node = self.matcher.match('Teacher', id=tea.id).first()
            if tea.image:
                src='http://127.0.0.1:8000/media/'+str(tea.image)
            else:
                src=None
            tea_node['image'] = src
            self.graph.push(tea_node)
            print(tea_node)

    def update_all(self,semester):
        month=semester.split('/')[1]
        # self.create_lesson_node()
        if month=='9':
            self.create_all_student_node()
            self.create_all_teacher_node()
            self.create_major_node()
            self.create_like_maj_rela()
            self.create_stu_maj_rela()
        self.select_schedule_lesson(semester=semester)

jwxzsgraph=JwxzsGraph()

if __name__ == '__main__':
    jwxzs_graph=JwxzsGraph()
    print(jwxzs_graph.graph.name)
    # jwxzs_graph.update_teacher_image()
    # jwxzs_graph.update_student_image()
    jwxzs_graph.update_lesson_node()
    # jwxzs_graph.find_lesson_tags('003912')
    # jwxzs_graph.create_major_node()
    # jwxzs_graph.select_schedule_lesson()
    # jwxzs_graph.create_stu_maj_rela()
    # jwxzs_graph.create_like_maj_rela()

    # jwxzs_graph.create_all_teacher_node()
    # jwxzs_graph.create_all_student_node()
    # jwxzs_graph.select_schedule_lesson()
    # jwxzs_graph.create_classmate_relation()
    # jwxzs_graph.test3()

    # jwxzs_graph.test()
    # jwxzs_graph.test2()

    # jwxzs_graph.select_schedule_lesson()
    # jwxzs_graph.create_node()
    # jwxzs_relation_graph.mat('Lesson')
    # jwxzs_graph.mat()

    # jwxzs_graph.create_node()
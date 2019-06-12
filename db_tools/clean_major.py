import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")  # project_name 项目名称
django.setup()
import jieba
from django.db.models import Q


from users.models import Major,Class



def test_count():
    cla=Class.objects.filter(Q(Q(name__startswith='15级')|Q(name__startswith='16级')|Q(name__startswith='17级')|Q(name__startswith='18级')|Q(name__startswith='14级')|Q(name__startswith='13级'))&(Q(name__endswith='班'))).count()
    # c=Class.objects.filter(Q(name__startswith='15级')|Q(name__startswith='16级')|Q(name__startswith='17级')|Q(name__startswith='18级')|Q(name__startswith='14级')|Q(name__startswith='13级')).count()
    c=Class.objects.filter(Q(name__startswith='15级')|Q(name__startswith='16级')|Q(name__startswith='17级')|Q(name__startswith='18级')).count()
    cl=Class.objects.all().count()
    print(cla)
    print(c)
    print(cl)
    return cla


def get_all_class():
    cla=Class.objects.all().order_by('id')
    return cla


def clean_name(name):
    try:
        int(name[0])
        class_name = name.replace('班', '').replace(' ','').replace('（免费师范生）','').replace('(免费师范生)','')
        try:
            int(class_name[-1])
            class_name = class_name[3:-1]
            try:
                int(class_name[-1])
                class_name=class_name[:-1]
            except:
                pass
        except:
            class_name = class_name[3:]
        class_name=class_name.replace('3','').replace('2','').replace('1','').replace('4','').replace('5','')
        # print(class_name)
        return class_name
    except:
        # print('None')
        if name!='退学':
            class_name = name.replace('班', '').replace(' ', '')
            return class_name
        else:
            return None


def check_major(name,grade):
    # jieba.cut()
    # early_name=name

    maj=Major.objects.filter(name=name,grade=grade)
    if maj:
        maj=maj[0]
        # print(maj.name)
        return maj
    else:
        replace_name=name.replace('(','（').replace(')','）')
        maj = Major.objects.filter(name=replace_name,grade=grade)
        if maj:
            maj=maj[0]
            # print(maj.name)
            return maj
        else:
            replace_name=name.replace('（','(').replace('）',')')
            maj=Major.objects.filter(name=replace_name,grade=grade)
            if maj:
                maj=maj[0]
                # print(maj.name)
                return maj
            else:
                words=jieba.cut(name,cut_all=True)
                if words:
                    dict={}
                    dict_maj={}
                    for wo in words:
                        majors=Major.objects.filter(grade=grade,name__icontains=wo)
                        if majors:
                            for maj in majors:
                                maj_name=maj.name
                                # print(maj_name)
                                try:
                                    dict[maj_name] += 1
                                except:
                                    dict[maj_name]=1
                                    dict_maj[maj_name]=maj
                            # print(wo)
                        else:
                            # print(majors)
                            # print(grade,wo)
                            pass
                    try:
                        max_maj_name=max(dict, key=dict.get)
                        # print(max_maj_name)
                        return dict_maj[max_maj_name]
                    except:
                        # words=jieba.cut(name)
                        # if words:
                        #     dict = {}
                        #     for wo in words:
                        #         print(wo)
                        #         majors = Major.objects.filter(grade=grade, name__icontains=wo)
                        #         print(majors)
                        #         if majors:
                        #             for maj in majors:
                        #                 maj_name = maj.name
                        #                 print(maj_name)
                        #                 # print(maj_name)
                        #                 try:
                        #                     dict[maj_name] += 1
                        #                 except:
                        #                     dict[maj_name] = 1
                        #             # print(wo)
                        #         else:
                        #             # print(majors)
                        #             # print(grade,wo)
                        #             pass
                        #     try:
                        #         max_maj_name = max(dict, key=dict.get)
                        #         # print(max_maj_name)
                        #         return max_maj_name
                        #     except:
                        #         print('None')
                        #         return None
                        # else:
                        print('no words')
                        return None

                        # print(dict)
                        # print(name,grade)
                        # return None
                else:
                    print('no words')
                    return None





def main():
    cla=get_all_class()
    count = 0
    for c in cla:
        name=c.name
        name=clean_name(name)
        if name:
            if c.grade>=15:
                maj=check_major(name,c.grade)
                if maj:
                    if not c.major:
                        c.major=maj
                        c.save()
                    print('清除：',name,'班级名：',c.name,' 预测专业：',maj)
                    count+=1
    print(count)


if __name__ == '__main__':
    # get_all_class()
    main()
    # test_count()






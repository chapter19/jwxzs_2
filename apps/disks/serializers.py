# -*- coding:utf-8 -*-
from rest_framework import serializers
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime

from .models import Disk, Folder, File, FileExtension, ShareLink, Label, FolderPath, ShareLinkFolderPath, \
    OpenFolderPath, ShareLinkFolder, ShareLinkFile,CheckedUser,CheckedUserLog
from utils.password import make_sharelink_word
from utils.aes import make_my_password, return_my_words
from jwxzs_2.settings import MEDIA_ROOT
from message.models import Message


class TimeEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj.strftime('%Y-%m-%d %H:%M'))
        return super(TimeEncoder, self).default(obj)

class DiskRetrieveSerializer(serializers.ModelSerializer):
    close_time=serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    create_time=serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    update_time=serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    class Meta:
        model = Disk
        fields = ['ower', 'size', 'used_size', 'if_close', 'close_time', 'if_disable', 'if_open', 'create_time',
                  'update_time', 'id']

class DiskCreateSerializer(serializers.ModelSerializer):
    ower_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    if_open = serializers.BooleanField(required=False, label='是否开放,默认不开放', help_text='是否开放，默认不开放', default=False)
    class Meta:
        model = Disk
        fields = ['ower_id', 'if_open']
    def create(self, validated_data):
        ower_id = validated_data.get('ower_id')
        disk = Disk.objects.filter(ower_id=ower_id)
        if disk:
            raise serializers.ValidationError({'detail': '你已经创建了一个硬盘了，不能再创建了！'})
        return super(DiskCreateSerializer, self).create(validated_data)

class DiskStatusSerializer(serializers.ModelSerializer):
    if_close = serializers.BooleanField(label='是否关闭(不再使用)', help_text='是否关闭(不再使用)', required=True)
    id=serializers.IntegerField(read_only=True)
    class Meta:
        model = Disk
        fields = ['if_close','id']
    def update(self, instance, validated_data):
        if_close = validated_data.get('if_close')
        if if_close != instance.if_close:
            instance.if_close = if_close
            if if_close:
                instance.close_time = datetime.now()
            else:
                instance.resume_time=datetime.now()
        else:
            raise serializers.ValidationError('你的网盘状态未更改！请检查输入')
        instance.save()
        return instance

def recursive_open_root_folder(if_open,root_folder=None,parent_folder_list=[]):
    new_list=[]
    if root_folder:
        new_list.append(root_folder)
        return recursive_open_root_folder(if_open=if_open,parent_folder_list=new_list)
    else:
        if parent_folder_list:
            for pa_fo in parent_folder_list:
                folders=Folder.objects.filter(parent_folder=pa_fo)
                pa_fo.if_open=if_open
                pa_fo.if_auto_open=if_open
                pa_fo.save()
                if folders:
                    for fo in folders:
                        new_list.append(fo)
                files=File.objects.filter(folder=pa_fo)
                if files:
                    for fi in files:
                        fi.if_open=False
                        fi.if_auto_open=False
                        fi.save()
            if new_list:
                recursive_open_root_folder(if_open=if_open,parent_folder_list=new_list)
            else:
                return None

class DiskOpenSerializer(serializers.ModelSerializer):
    if_open=serializers.BooleanField(label='是否开放',help_text='是否开放',required=True)
    id=serializers.IntegerField(read_only=True)
    class Meta:
        model=Disk
        fields=['if_open','id']
    def update(self, instance, validated_data):
        if_open=validated_data.get('if_open')
        if if_open!=instance.if_open:
            instance.if_open=if_open
            root_files=File.objects.filter(disk=instance,folder=None)
            if root_files:
                for file in root_files:
                    file.if_open=False
                    file.if_auto_open=False
                    file.save()
            root_folders=Folder.objects.filter(disk=instance,parent_folder=None)
            if root_files:
                for folder in root_folders:
                    recursive_open_root_folder(if_open=if_open,root_folder=folder)
        else:
            raise serializers.ValidationError({'detail':'硬盘开放状态未改变！请检查输入'})
        instance.save()
        return instance

class LabelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'

class LabelCreateSerializer(serializers.Serializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    id = serializers.IntegerField(read_only=True, label='id', help_text='id')
    class Meta:
        model = Label
        fields = ['name', 'user_id', 'id']
    def create(self, validated_data):
        name = validated_data.get('name')
        label = Label.objects.filter(name=name)
        if label:
            raise serializers.ValidationError({'detail': '标签已存在！直接选择无需再创建'})
        else:
            user_id = validated_data.get('user_id')
            label = Label.objects.create(name=name, create_user_id=user_id)
            return label

class FolderListSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M', label='创建时间', help_text='创建时间')
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M', label='修改时间', help_text='修改时间')
    delete_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M', label='回收时间', help_text='回收时间')
    resume_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M', label='恢复时间', help_text='恢复时间')
    label=LabelListSerializer(many=True,label='标签',help_text='标签')
    auto_label=LabelListSerializer(many=True,label='继承父文件夹标签的标签',help_text='继承父文件夹标签的标签')
    class Meta:
        model = Folder
        fields = ['name', 'parent_folder', 'create_time', 'update_time', 'disk', 'if_open', 'if_delete',
                  'delete_time', 'resume_time', 'id','label','auto_label','file_count','if_auto_delete','if_auto_open',
                   'if_clone','if_auto_clone','click_count','clone_count','if_auto_resume','clone_from']

class FolderPathSerializer(serializers.ModelSerializer):
    folder=FolderListSerializer()
    class Meta:
        model=FolderPath
        fields=['num','folder','path_folder_id','path_folder_name']

class OpenFolderPathSerializer(serializers.ModelSerializer):
    folder = FolderListSerializer()
    class Meta:
        model=OpenFolderPath
        fields=['num','folder','path_folder_id','path_folder_name']

class ShareLinkFolderPathSerializer(serializers.ModelSerializer):
    class Meta:
        model=ShareLinkFolderPath
        fields=['num','sharelink_folder','path_folder_id','path_folder_name']

class FolderCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, default='未命名', label='文件夹名', help_text='文件夹名', max_length=50,initial='未命名')
    parent_folder_id = serializers.UUIDField(required=False, label='父文件夹id', help_text='父文件夹id', default=None)
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    if_open = serializers.BooleanField(required=True, label='是否公开,默认不公开', help_text='是否公开,默认不公开')
    id = serializers.UUIDField(read_only=True, label='id', help_text='id')
    label_id_list = serializers.ListField(child=serializers.IntegerField(), label='标签id列表', help_text='标签id列表',required=False)
    class Meta:
        model = Folder
        fields = ['name', 'parent_folder_id', 'user_id', 'if_open', 'id', 'label_id_list']
    def create(self, validated_data):
        folder = Folder()
        label_id_list = validated_data.get('label_id_list')
        if label_id_list:
            le = len(label_id_list)
            if le <= 5:
                if le > len(set(label_id_list)):
                    raise serializers.ValidationError({'detail': '标签id不能重复！'})
                else:
                    for lab_id in label_id_list:
                        label = Label.objects.filter(id=lab_id)
                        if label:
                            folder.label.add(label)
                        else:
                            raise serializers.ValidationError({'detail': '标签不存在！请检查并重新输入'})
            else:
                raise serializers.ValidationError({'detail': '标签不能超过五个！'})
        user_id = validated_data.get('user_id')
        if_open = validated_data.get('if_open')
        disk = Disk.objects.filter(ower_id=user_id)
        if disk:
            disk = disk[0]
            if disk.if_disable:
                raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再继续使用'})
            if disk.if_close:
                raise serializers.ValidationError({'detail': '你的网盘已关闭，先去开启再继续使用吧！'})
            folder.disk = disk
            if disk.if_open:
                if if_open:
                    folder.if_open = True
                    folder.if_auto_open = True
                elif if_open == False:
                    raise serializers.ValidationError({'detail': '该网盘已开放，当前文件夹设置不开放无效！'})
            else:
                folder.if_open = if_open
            disk.folder_count += 1
        else:
            raise serializers.ValidationError({'detail': '你还没有创建网盘，先去创建网盘吧'})
        parent_folder_id = validated_data.get('parent_folder_id')
        name = validated_data.get('name')
        if name:
            folder.name = name
        else:
            folder.name = '未命名'
        if parent_folder_id:
            parent_folder = Folder.objects.filter(id=parent_folder_id)
            if parent_folder:
                parent_folder = parent_folder[0]
                if parent_folder.if_delete:
                    raise serializers.ValidationError({'detail': '该父文件夹已回收，先去回收箱恢复再操作吧！'})
                if parent_folder.if_open:
                    if if_open:
                        folder.if_open = True
                        folder.if_auto_open = True
                    elif if_open == False:
                        raise serializers.ValidationError({'detail': '父文件夹已开放，设置该文件夹不开放无效！'})
                else:
                    folder.if_open = if_open
                fo = Folder.objects.filter(parent_folder=parent_folder, name=folder.name)
                if fo:
                    l = len(fo)
                    folder.name += '(%d)' % l
                folder.parent_folder=parent_folder
                parent_labels = parent_folder.label.all()
                if parent_labels:
                    for lab in parent_labels:
                        folder.auto_label.add(lab)
                folder.save()
                parent_path = FolderPath.objects.filter(folder=parent_folder).order_by('num')
                if parent_path:
                    num = 1
                    for p_pa in parent_path:
                        num += 1
                        FolderPath.objects.create(num=p_pa.num, path_folder_id=p_pa.path_folder_id,path_folder_name=p_pa.path_folder_name, folder=folder)
                    FolderPath.objects.create(num=num, path_folder_name=folder.name, path_folder_id=folder.id,folder=folder)
                else:
                    raise serializers.ValidationError({'detail': '路径异常'})
                if parent_folder.if_open:
                    open_path = OpenFolderPath.objects.filter(folder=parent_folder)
                    if open_path:
                        num = 1
                        for o_p in open_path:
                            num += 1
                            OpenFolderPath.objects.create(num=o_p.num, folder=folder, path_folder_id=o_p.path_folder_id,path_folder_name=o_p.path_folder_name)
                        OpenFolderPath.objects.create(num=num, folder=folder, path_folder_id=folder.id,path_folder_name=name)
                disk.save()
                sharelink_folder=ShareLinkFolder.objects.filter(original_folder=parent_folder,sharelink__if_synchro=True,sharelink__status='normal')
                if sharelink_folder:
                    for sh_fo in sharelink_folder:
                        new_sharelink_folder=ShareLinkFolder.objects.create(name=folder.name,original_folder=folder,parent_sharelink_folder=sh_fo,sharelink=sh_fo.sharelink)
                        labels=Label.objects.filter(my_folder=folder)
                        if labels:
                            for lab in labels:
                                new_sharelink_folder.label.add(lab)
                        auto_labels=Label.objects.filter(my_auto_folder=folder)
                        if auto_labels:
                            for auto_lab in auto_labels:
                                new_sharelink_folder.auto_label.add(auto_lab)
                        new_sharelink_folder.save()
                        sh_fo.child_sharelink_folder_count += 1
                        sh_fo.save()
            else:
                raise serializers.ValidationError({'detail': '文件夹不存在！'})
        else:
            fo = Folder.objects.filter(parent_folder=None, name=name)
            if fo:
                l = len(fo)
                folder.name += '(%d)' % l
            folder.save()
            disk.root_folder_count += 1
            disk.save()
            FolderPath.objects.create(path_folder_name=folder.name, path_folder_id=folder.id, folder=folder)
            if disk.if_open:
                OpenFolderPath.objects.create(folder=folder, path_folder_id=folder.id, path_folder_name=folder.name)
        return folder

def recursive_clone_open_folder(if_open,disk,cloned_folder=None,parent_folder=None,cloned_folder_list=[],parent_folder_list=[],returned_folder=None):
    cl_fo_list=[]
    pa_fo_list=[]
    if cloned_folder:
        if parent_folder:
            cl_fo_list.append(cloned_folder)
            pa_fo_list.append(parent_folder)
        else:
            if disk.if_open:
                folder=Folder.objects.create(name=cloned_folder.name,disk=disk,if_open=True,if_auto_open=True,if_clone=True,clone_from=cloned_folder)
            else:
                folder=Folder.objects.create(name=cloned_folder.name,disk=disk,if_open=if_open,if_clone=True,clone_from=cloned_folder)
            labels = Label.objects.filter(my_folder=cloned_folder)
            if labels:
                for lab in labels:
                    folder.label.add(lab)
            auto_labels = Label.objects.filter(my_auto_folder=cloned_folder)
            if auto_labels:
                for auto_lab in auto_labels:
                    folder.auto_label.add(auto_lab)
            folder.save()
            cloned_folder.clone_count+=1
            cloned_folder.save()
        return recursive_clone_open_folder(if_open=if_open,disk=disk,cloned_folder_list=cl_fo_list,parent_folder_list=pa_fo_list,returned_folder=folder)
    else:
        if cloned_folder_list:
            for cl_fo,pa_fo in zip(cloned_folder_list,parent_folder_list):
                child_cloned_folders=Folder.objects.filter(parent_folder=cl_fo,if_delete=False)
                if child_cloned_folders:
                    for ch_cl_fo in child_cloned_folders:
                        if pa_fo.if_open:
                            new_ch_fo=Folder.objects.create(name=ch_cl_fo.name,disk=disk,if_open=True,if_auto_open=True,if_clone=True,if_auto_clone=True,clone_from=ch_cl_fo)
                        else:
                            new_ch_fo=Folder.objects.create(name=ch_cl_fo.name,disk=disk,if_open=if_open,if_clone=True,if_auto_clone=True,clone_from=ch_cl_fo)
                        labels = Label.objects.filter(my_folder=ch_cl_fo)
                        if labels:
                            for lab in labels:
                                new_ch_fo.label.add(lab)
                        auto_labels = Label.objects.filter(my_auto_folder=ch_cl_fo)
                        if auto_labels:
                            for auto_lab in auto_labels:
                                new_ch_fo.auto_label.add(auto_lab)
                        new_ch_fo.save()
                        ch_cl_fo.clone_count+=1
                        ch_cl_fo.save()
                        cl_fo_list.append(ch_cl_fo)
                        pa_fo_list.append(new_ch_fo)
                else:
                    pass
                cloned_files=File.objects.filter(folder=cl_fo,if_delete=False)
                if cloned_files:
                    for cl_fi in cloned_files:
                        if (disk.used_size+cl_fi.size)<=disk.size:
                            if pa_fo.if_open:
                                fi=File.objects.create(name=cl_fi.name,disk=disk,file=cl_fi.file,size=cl_fi.size,extension=cl_fi.extension,thumbnail=cl_fi.thumbnail,if_open=True,if_auto_open=True,if_clone=True,if_auto_clone=True,clone_from=cl_fi)
                            else:
                                fi=File.objects.create(name=cl_fi.name,disk=disk,file=cl_fi.file,size=cl_fi.size,extension=cl_fi.extension,thumbnail=cl_fi.thumbnail,if_open=if_open,if_clone=True,if_auto_clone=True,clone_from=cl_fi)
                            labels = Label.objects.filter(my_file=cl_fi)
                            if labels:
                                for lab in labels:
                                    fi.label.add(lab)
                            auto_labels = Label.objects.filter(my_auto_file=cl_fi)
                            if auto_labels:
                                for auto_lab in auto_labels:
                                    fi.auto_label.add(auto_lab)
                            fi.save()
                            cl_fi.clone_count+=1
                            cl_fi.save()
                        else:
                            raise serializers.ValidationError({'detail':'你的网盘已满！克隆终止'})
            return recursive_clone_open_folder(if_open=if_open,disk=disk,cloned_folder_list=cl_fo_list,parent_folder_list=pa_fo_list,returned_folder=returned_folder)
        else:
            return returned_folder

def recursive_clone_sharelink_folder(if_open,disk,cloned_sharelink_folder=None,parent_folder=None,cloned_sharelink_folder_list=[],parent_folder_list=[],returned_folder=None):
    cl_sh_fo_list = []
    pa_fo_list = []
    if cloned_sharelink_folder:
        if parent_folder:
            cl_sh_fo_list.append(cloned_sharelink_folder)
            pa_fo_list.append(parent_folder)
        else:
            if disk.if_open:
                folder = Folder.objects.create(name=cloned_sharelink_folder.name, disk=disk, if_open=True, if_auto_open=True,
                                               if_clone=True)
            else:
                folder = Folder.objects.create(name=cloned_sharelink_folder.name, disk=disk, if_open=if_open, if_clone=True,)
            labels = Label.objects.filter(sharelink_folder=cloned_sharelink_folder)
            if labels:
                for lab in labels:
                    folder.label.add(lab)
            auto_labels = Label.objects.filter(sharelink_auto_folder=cloned_sharelink_folder)
            if auto_labels:
                for auto_lab in auto_labels:
                    folder.auto_label.add(auto_lab)
            folder.save()
            cloned_sharelink_folder.clone_count += 1
            cloned_sharelink_folder.save()
        return recursive_clone_sharelink_folder(if_open=if_open, disk=disk, cloned_sharelink_folder_list=cl_sh_fo_list,parent_folder_list=pa_fo_list,returned_folder=folder)
    else:
        if cloned_sharelink_folder_list:
            for cl_sh_fo, pa_fo in zip(cloned_sharelink_folder_list, parent_folder_list):
                child_cloned_sharelink_folders = ShareLinkFolder.objects.filter(parent_sharelink_folder=cl_sh_fo, if_delete=False)
                if child_cloned_sharelink_folders:
                    for ch_cl_sh_fo in child_cloned_sharelink_folders:
                        if pa_fo.if_open:
                            new_ch_fo = Folder.objects.create(name=ch_cl_sh_fo.name, disk=disk, if_open=True,if_auto_open=True, if_clone=True, if_auto_clone=True)
                        else:
                            new_ch_fo = Folder.objects.create(name=ch_cl_sh_fo.name, disk=disk, if_open=if_open,
                                                              if_clone=True, if_auto_clone=True)
                        labels = Label.objects.filter(sharelink_folder=ch_cl_sh_fo)
                        if labels:
                            for lab in labels:
                                new_ch_fo.label.add(lab)
                        auto_labels = Label.objects.filter(sharelink_auto_folder=ch_cl_sh_fo)
                        if auto_labels:
                            for auto_lab in auto_labels:
                                new_ch_fo.auto_label.add(auto_lab)
                        new_ch_fo.save()
                        ch_cl_sh_fo.clone_count += 1
                        ch_cl_sh_fo.save()
                        cl_sh_fo_list.append(ch_cl_sh_fo)
                        pa_fo_list.append(new_ch_fo)
                else:
                    pass
                cloned_sharelink_files = ShareLinkFile.objects.filter(sharelink_folder=cl_sh_fo, if_delete=False)
                if cloned_sharelink_files:
                    for cl_sh_fi in cloned_sharelink_files:
                        if (disk.size+cl_sh_fi.size)<=disk.size:
                            if pa_fo.if_open:
                                fi = File.objects.create(name=cl_sh_fi.name, disk=disk, file=cl_sh_fi.file, size=cl_sh_fi.size,
                                                         extension=cl_sh_fi.extension, thumbnail=cl_sh_fi.thumbnail, if_open=True,
                                                         if_auto_open=True, if_clone=True, if_auto_clone=True)
                            else:
                                fi = File.objects.create(name=cl_sh_fi.name, disk=disk, file=cl_sh_fi.file, size=cl_sh_fi.size,
                                                         extension=cl_sh_fi.extension, thumbnail=cl_sh_fi.thumbnail,
                                                         if_open=if_open, if_clone=True, if_auto_clone=True)
                            labels = Label.objects.filter(sharelink_file=cl_sh_fi)
                            if labels:
                                for lab in labels:
                                    fi.label.add(lab)
                            auto_labels = Label.objects.filter(sharelink_auto_file=cl_sh_fi)
                            if auto_labels:
                                for auto_lab in auto_labels:
                                    fi.auto_label.add(auto_lab)
                            fi.save()
                            cl_sh_fi.clone_count += 1
                            cl_sh_fi.save()
            return recursive_clone_sharelink_folder(if_open=if_open, disk=disk, cloned_sharelink_folder_list=cl_sh_fo_list,parent_folder_list=pa_fo_list,returned_folder=returned_folder)
        else:
            return returned_folder

class FolderCloneSerializer(serializers.Serializer):
    id_list=serializers.ListField(child=serializers.UUIDField(),write_only=True,allow_empty=False,label='被克隆的文件夹id列表',help_text='被克隆的文件夹id列表',required=True)
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    parent_folder_id=serializers.UUIDField(required=False,label='要克隆到哪个父文件夹下',help_text='要克隆到哪个父文件夹下',write_only=True)
    from_open_or_share_link=serializers.ChoiceField(choices=(('open_folder','公开文件夹'),('share_link','分享的文件夹')),required=True,label='克隆文件夹来源',help_text='克隆文件夹来源',write_only=True)
    if_open=serializers.BooleanField(required=False,label='是否公开，默认公开',help_text='是否公开',write_only=True)
    class Meta:
        model=Folder
        fields=['id_list','user_id','from_open_or_share_link','parent_folder_id','if_open']
    def create(self, validated_data):
        user_id=validated_data.get('user_id')
        disk=Disk.objects.filter(ower_id=user_id)
        if not disk:
            raise serializers.ValidationError({'detail':'你还没有创建网盘！先去创建网盘吧'})
        disk = disk[0]
        if disk.if_disable:
            raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再继续使用'})
        if disk.if_close:
            raise serializers.ValidationError({'detail': '你的网盘已关闭，先去开启再继续使用吧！'})
        parent_folder_id=validated_data.get('parent_folder_id')
        if parent_folder_id:
            parent_folder=Folder.objects.filter(id=parent_folder_id)
            if not parent_folder:
                raise serializers.ValidationError({'detail':'该文件夹不存在！'})
            else:
                parent_folder=parent_folder[0]
                if parent_folder.if_delete:
                    raise serializers.ValidationError({"detail":'该文件夹已回收！'})
                else:
                    pass
        else:
            pass
        if_open=validated_data.get('if_open')
        id_list=validated_data.get('id_list')
        from_open_or_share_link=validated_data.get('from_open_or_share_link')
        if from_open_or_share_link=='open_folder':
            for id in id_list:
                folder=Folder.objects.filter(id=id,if_delete=False)
                if folder:
                    folder=folder[0]
                    if folder.if_open:
                        if parent_folder_id:
                            returned_folder =recursive_clone_open_folder(disk=disk,if_open=if_open,cloned_folder=folder,parent_folder=parent_folder)
                        else:
                            returned_folder =recursive_clone_open_folder(disk=disk,if_open=True,cloned_folder=folder)
                    else:
                        raise serializers.ValidationError({'detail':'该文件夹未开放，你不能克隆！'})
                else:
                    raise serializers.ValidationError({'detail':'该文件夹不存在或已被回收！请检查并重新输入'})
        elif from_open_or_share_link=='share_link':
            for id in id_list:
                sharelink_folder=ShareLinkFolder.objects.filter(id=id,if_delete=False)
                if sharelink_folder:
                    sharelink_folder=sharelink_folder[0]
                    sharelink=sharelink_folder.sharelink
                    checked=CheckedUser.objects.filter(share_link=sharelink,user_id=user_id)
                    if checked:
                        checked=checked[0]
                        if checked.if_disable:
                            raise serializers.ValidationError({'detail':'你已被分享者禁用该链接！不能再克隆该文件'})
                        else:
                            if sharelink.time_limit == None:
                                pass
                            elif sharelink.time_limit > datetime.now():
                                pass
                            else:
                                raise serializers.ValidationError({'detail': '该分享链接已过期，你不能再克隆！'})
                            if parent_folder_id:
                                returned_folder=recursive_clone_sharelink_folder(disk=disk,cloned_sharelink_folder=sharelink_folder,parent_folder=parent_folder)
                            else:
                                returned_folder =recursive_clone_sharelink_folder(disk=disk,cloned_sharelink_folder=sharelink_folder)
                    else:
                        raise serializers.ValidationError({'detail':'你没有通过该分享链接的认证，先去找分享者获取链接和密码吧！'})
                else:
                    raise serializers.ValidationError({'detail':'某个文件夹不存在或已被回收！克隆终止，请重新输入！'})
        return returned_folder

class FolderNameUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True,label='文件夹名', help_text='文件夹名', max_length=50)
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    id=serializers.UUIDField(read_only=True)
    class Meta:
        model=Folder
        fields=['name','user_id','id']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        disk = Disk.objects.filter(ower_id=user_id)
        disk = disk[0]
        if disk.if_disable:
            raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再继续使用'})
        if disk.if_close:
            raise serializers.ValidationError({'detail': '你的网盘已关闭，先去开启再继续使用吧！'})
        name=validated_data.get('name')
        if instance.name!=name:
            instance.name=name
        else:
            raise serializers.ValidationError({'detail':'文件名未修改！请检查输入'})
        instance.save()
        return instance

def recursive_update_folder_path(new_parent_folder=None,folder=None,parent_folder_list=[],if_open=None):
    pa_fo_li=[]
    if folder:
        i_o = None
        if new_parent_folder:
            folder.parent_folder.child_folder_count-=1
            folder.parent_folder.save()
            folder.parent_folder=new_parent_folder
            folder.parent_folder.child_folder_count += 1
            folder.parent_folder.save()
            if new_parent_folder.if_open:
                folder.if_open=True
                folder.if_auto_open=True
            else:
                if (folder.if_open) and (folder.if_auto_open==False):
                    i_o=True
                else:
                    folder.if_open=False
            folder.save()
            FolderPath.objects.filter(folder=folder).delete()
            path=FolderPath.objects.filter(folder=new_parent_folder)
            if path:
                num=1
                for p in path:
                    num+=1
                    FolderPath.objects.create(num=p.num,folder=folder,path_folder_name=p.name,path_folder_id=p.id)
                FolderPath.objects.create(num=num,folder=folder,path_folder_name=folder.name,path_folder_id=folder.id)
        else:
            folder.parent_folder.child_folder_count-=1
            folder.parent_folder.save()
            disk = folder.disk
            disk.root_folder_count+=1
            disk.save()
            if disk.if_open:
                folder.if_open=True
            else:
                if (folder.if_open) and (folder.if_auto_open==False):
                    i_o=True
                else:
                    folder.if_open=False
            folder.parent_folder=None
            folder.save()
            FolderPath.objects.filter(folder=folder).delete()
            FolderPath.objects.create(folder=folder,path_folder_id=folder.id,path_folder_name=folder.name)
        pa_fo_li.append(folder)
        return recursive_update_folder_path(parent_folder_list=pa_fo_li,if_open=i_o)
    else:
        if parent_folder_list:
            for parent_folder in parent_folder_list:
                parent_folder_path=FolderPath.objects.filter(folder=parent_folder)
                child_folder=Folder.objects.filter(parent_folder=parent_folder)
                if child_folder:
                    for c_f in child_folder:
                        if if_open:
                            pass
                        else:
                            if parent_folder.if_open:
                                c_f.if_open=True
                                c_f.if_auto_open=True
                            else:
                                c_f.if_open=False
                                c_f.if_auto_open=False
                        c_f.save()
                        FolderPath.objects.filter(folder=c_f).delete()
                        pa_fo_li.append(c_f)
                        num=1
                        for p_f_p in parent_folder_path:
                            FolderPath.objects.create(folder=c_f,num=p_f_p.num,path_folder_id=p_f_p.path_folder_id,path_folder_name=p_f_p.path_folder_name)
                            num+=1
                        FolderPath.objects.create(folder=c_f,num=num,path_folder_id=c_f.id,path_folder_name=c_f.name)
                file=File.objects.filter(folder=parent_folder)
                if file:
                    if if_open:
                        pass
                    else:
                        for fi in file:
                            if parent_folder.if_open:
                                fi.if_open=True
                                fi.if_auto_open=True
                            else:
                                fi.if_open=False
                                fi.if_auto_open=False

            if pa_fo_li:
                return recursive_update_folder_path(parent_folder_list=pa_fo_li,if_open=if_open)
            else:
                return None

class FolderParentFolderUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    parent_folder_id = serializers.UUIDField(required=False, label='父文件夹id', help_text='父文件夹id')
    id=serializers.UUIDField(read_only=True)
    class Meta:
        model=Folder
        fields=['parent_folder_id','user_id','id']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        disk = Disk.objects.filter(ower_id=user_id)
        disk = disk[0]
        if disk.if_disable:
            raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再继续使用'})
        if disk.if_close:
            raise serializers.ValidationError({'detail': '你的网盘已关闭，先去开启再继续使用吧！'})
        parent_folder_id=validated_data.get('parent_folder_id')
        if parent_folder_id:
            if instance.parent_folder_id!=parent_folder_id:
                parent_folder=Folder.objects.filter(id=parent_folder_id,if_delete=False)
                if parent_folder:
                    parent_folder=parent_folder[0]
                    if parent_folder.disk==instance.disk:
                        child_folder=Folder.objects.filter(name=instance.name,parent_folder=parent_folder)
                        if child_folder:
                            raise serializers.ValidationError({'detail':'该文件夹存在同名子文件夹！先修改文件夹名吧'})
                        else:
                            recursive_update_folder_path(new_parent_folder=parent_folder,folder=instance)
                    else:
                        raise serializers.ValidationError({"detail":"你的文件夹不能挂在别人的网盘下！"})
                else:
                    raise serializers.ValidationError({'detail':'该文件夹不存在或已被回收！请重新输入'})
            else:
                raise serializers.ValidationError({'detail':'文件夹未修改！请检查输入'})
        else:
            if instance.parent_folder:
                recursive_update_folder_path(folder=instance)
            else:
                raise serializers.ValidationError({'detail':'该文件夹位置未改变！'})
        instance.save()
        return instance

def recursive_update_folder_if_open(folder,if_open,parent_folder_list=[]):
    pa_fo_li=[]
    if folder:
        folder.if_open=if_open
        folder.save()
        pa_fo_li.append(folder)
        return recursive_update_folder_if_open(if_open=if_open,parent_folder_list=pa_fo_li)
    else:
        if parent_folder_list:
            for parent_folder in parent_folder_list:
                folder=Folder.objects.filter(parent_folder=parent_folder)
                if folder:
                    for fo in folder:
                        if if_open:
                            fo.if_open=True
                            fo.if_auto_open=True
                        else:
                            fo.if_open=False
                        fo.save()
                        pa_fo_li.append(fo)
            if pa_fo_li:
                return recursive_update_folder_if_open(if_open=if_open,parent_folder_list=pa_fo_li)
            else:
                return None

class FolderIfOpenUpdateSerializer(serializers.Serializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    if_open = serializers.UUIDField(required=True, label='是否开放', help_text='是否开放')
    id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Folder
        fields = ['if_open', 'user_id', 'id']

    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        disk = Disk.objects.filter(ower_id=user_id)
        disk = disk[0]
        if disk.if_disable:
            raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再继续使用'})
        if disk.if_close:
            raise serializers.ValidationError({'detail': '你的网盘已关闭，先去开启再继续使用吧！'})
        if_open=validated_data.get('if_open')
        parent_folder=instance.parent_folder
        if instance.if_open:
            if if_open:
                raise serializers.ValidationError({'detail':'文件夹开放状态未改变！请检查并重新输入'})
            else:
                if parent_folder:
                    if parent_folder.if_open:
                        raise serializers.ValidationError({'detail':'父文件夹已开放！设置当前文件夹不开放无效'})
                    else:
                        recursive_update_folder_if_open(folder=instance,if_open=if_open)
                else:
                    disk=instance.disk
                    if disk.if_open:
                        raise serializers.ValidationError({'detail':'你的网盘已开放！设置当前文件夹不开放无效'})
                    else:
                        recursive_update_folder_if_open(folder=instance,if_open=False)
        else:
            if if_open:
                recursive_update_folder_if_open(folder=instance, if_open=True)
            else:
                raise serializers.ValidationError({'detail':'该文件夹开放状态未改变！请检查并重新输入'})
        return instance

def recursive_update_folder_if_delete(if_delete,folder=None,parent_folder_list=[]):
    pa_fo_li=[]
    if folder:
        if if_delete:
            folder.if_delete=True
            folder.delete_time=datetime.now()
        else:
            folder.if_delete=False
            folder.resume_time=datetime.now()
        folder.save()
        pa_fo_li.append(folder)
        return recursive_update_folder_if_delete(if_delete=if_delete,parent_folder_list=pa_fo_li)
    else:
        if parent_folder_list:
            for parent_folder in parent_folder_list:
                folders=Folder.objects.filter(parent_folder=parent_folder)
                if folders:
                    if if_delete:
                        for fo in folders:
                            fo.if_delete=True
                            fo.if_auto_delete=True
                            fo.delete_time=datetime.now()
                            fo.save()
                            pa_fo_li.append(fo)
                    else:
                        for fo in folders:
                            fo.if_delete=False
                            fo.if_auto_resume=True
                            fo.resume_time=datetime.now()
                            fo.save()
                            pa_fo_li.append(fo)
            if pa_fo_li:
                return recursive_update_folder_if_delete(if_delete=if_delete,parent_folder_list=pa_fo_li)
            else:
                return None

class FolderIfDeleteSerializer(serializers.Serializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    if_delete = serializers.UUIDField(required=True, label='是否回收', help_text='是否回收')
    id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Folder
        fields = ['if_delete', 'user_id', 'id']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        disk = Disk.objects.filter(ower_id=user_id)
        disk = disk[0]
        if disk.if_disable:
            raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再继续使用'})
        if disk.if_close:
            raise serializers.ValidationError({'detail': '你的网盘已关闭，先去开启再继续使用吧！'})
        if_delete=validated_data.get('if_delete')
        parent_folder=instance.parent_folder
        if instance.if_delete:
            if if_delete:
                raise serializers.ValidationError({'detail':'该文件夹已被回收！请勿重复操作！先去恢复吧'})
            else:
                if parent_folder:
                    if parent_folder.if_delete:
                        raise serializers.ValidationError({'detail':'父文件夹已被回收！该操作无效！请直接恢复父文件夹'})
                    else:
                        recursive_update_folder_if_delete(folder=instance,if_delete=False)
                else:
                    recursive_update_folder_if_delete(folder=instance, if_delete=if_delete)
        else:
            if if_delete:
                return recursive_update_folder_if_delete(folder=instance,if_delete=True)
            else:
                raise serializers.ValidationError({'detail':'该文件夹未被回收！无需恢复'})
        return instance

class FileExtensionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileExtension
        fields = ['name', 'type']

class FileExtensionTypeSerializer(serializers.Serializer):
    def create(self, validated_data):
        data = FileExtension.objects.all().values('type').distinct()
        return data

class FileListSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M', help_text='创建时间', label='创建时间')
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M', help_text='修改时间', label='修改时间')
    delete_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M', help_text='回收时间', label='回收时间')
    resume_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M', help_text='恢复时间', label='恢复时间')
    class Meta:
        model = File
        exclude=['file']

class FileCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    if_open = serializers.BooleanField(label='是否开放，默认不开放', help_text='是否开放，默认不开放', required=False)
    folder_id = serializers.UUIDField(label='文件夹id', help_text='文件夹id', required=False)
    name = serializers.CharField(max_length=50, label='文件名', help_text='文件名', required=False)
    id = serializers.UUIDField(read_only=True, label='id', help_text='id')
    verbose_id = serializers.UUIDField(read_only=True, label='verbose_id', help_text='verbose_id')
    label_id_list = serializers.ListField(child=serializers.IntegerField(), label='标签id列表', help_text='标签id列表',allow_empty=True,required=False)
    class Meta:
        model = File
        fields = ['user_id', 'if_open', 'folder_id', 'file', 'name', 'label_id_list', 'id','verbose_id']

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        file = validated_data.get('file')
        fil = File()
        disk = Disk.objects.filter(ower_id=user_id)
        if_open = validated_data.get('if_open')
        name = validated_data.get('name')
        label_id_list = validated_data.get('label_id_list')
        if label_id_list:
            le = len(label_id_list)
            if le <= 5:
                if le > len(set(label_id_list)):
                    raise serializers.ValidationError({'detail': '标签id不能重复！'})
                else:
                    for lab_id in label_id_list:
                        label = Label.objects.filter(id=lab_id)
                        if label:
                            fil.label.add(label)
                        else:
                            raise serializers.ValidationError({'detail': '标签不存在！请检查并重新输入'})
            else:
                raise serializers.ValidationError({'detail': '标签不能超过五个！'})
        if disk:
            disk = disk[0]
            if disk.if_disable:
                raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再继续使用'})
            if disk.if_close:
                raise serializers.ValidationError({'detail': '你的网盘已关闭，先去开启再继续使用吧！'})
            fil.disk = disk
            if disk.if_open:
                if if_open:
                    fil.if_open = True
                    fil.if_auto_open = True
                elif if_open == False:
                    raise serializers.ValidationError({'detail': '该网盘已开放，当前文件夹设置不开放无效！'})
            else:
                fil.if_open = if_open
            f_s = file.size
            if disk.used_size + f_s > disk.size:
                file.delete()
                raise serializers.ValidationError({'detail': '超过网盘大小！先去删除一部分文件或清空回收箱吧'})
            else:
                fil.file=file
                disk.used_size += f_s
                disk.file_count += 1
        else:
            raise serializers.ValidationError({'detail': '你还没有创建网盘，先去创建网盘吧'})
        if name:
            fil.name = name
        fil.size = f_s
        folder_id = validated_data.get('folder_id')
        if folder_id:
            folder = Folder.objects.filter(id=folder_id)
            if folder:
                folder = folder[0]
                if folder.if_delete:
                    raise serializers.ValidationError({'detail': '该文件夹已回收！请先从回收箱恢复或重新选择'})
                else:
                    fil.folder = folder
                    if folder.if_open:
                        if if_open:
                            fil.if_open = True
                            fil.if_auto_open = True
                        else:
                            raise serializers.ValidationError({'detail': '父文件夹已开放，设置该文件不开放无效！'})
                    else:
                        fil.if_open = if_open
                    folder_labels = folder.label.all()
                    if folder_labels:
                        for lab in folder_labels:
                            fil.auto_label.add(lab)
                    fi = File.objects.filter(folder=folder, name=fil.name)
                    if fi:
                        l = len(fi)
                        fil.name += '(%d)' % l
                    folder.file_count += 1
                    folder.save()
                    fil.save()
                    disk.save()

                    sharelink_folder = ShareLinkFolder.objects.filter(original_folder=folder,sharelink__if_synchro=True)
                    if sharelink_folder:
                        for sh_fo in sharelink_folder:
                            new_sharelink_file = ShareLinkFile.objects.create(name=fil.name,original_file=fil,sharelink_folder=sh_fo,sharelink=sh_fo.sharelink)
                            labels = Label.objects.filter(my_file=fil)
                            if labels:
                                for lab in labels:
                                    new_sharelink_file.label.add(lab)
                            auto_labels = Label.objects.filter(my_auto_file=fil)
                            if auto_labels:
                                for auto_lab in auto_labels:
                                    new_sharelink_file.auto_label.add(auto_lab)
                            new_sharelink_file.save()
                            sh_fo.file_count += 1
                            sh_fo.save()
            else:
                raise serializers.ValidationError({'detail': '该文件夹不存在！请重新选择'})
        else:
            fi = File.objects.filter(folder=None, name=fil.name)
            if fi:
                l = len(fi)
                fil.name += '(%d)' % l
            fil.save()
            disk.root_file_count += 1
            disk.save()
        # file_extension=fil.extension
        # file_extension.file_count+=1
        # file_extension.save()
        return fil

class FileCloneSerializer(serializers.Serializer):
    file_from=serializers.ChoiceField(choices=(('open_file','公开文件'),('sharelink','分享链接')),label='文件来源',help_text='文件来源',write_only=True,required=True)
    id_list=serializers.ListField(child=serializers.UUIDField(),write_only=True,required=True,label='文件id列表',help_text='文件id列表',allow_empty=False)
    folder_id=serializers.UUIDField(required=False,label='文件夹id',help_text='文件夹id',write_only=True)
    user_id=serializers.HiddenField(default=serializers.CurrentUserDefault())
    if_open=serializers.BooleanField(required=True,label='是否公开',help_text='是否公开',write_only=True)
    class Meta:
        model=File
        fields=['file_from','id_list','folder_id','user_id','if_open','id']
    def create(self, validated_data):
        user_id=validated_data.get('user_id')
        disk=Disk.objects.filter(ower_id=user_id)
        if not disk:
            raise serializers.ValidationError({'detail':'你还没有创建网盘，先去创建网盘吧！'})
        disk=disk[0]
        if disk.if_disable:
            raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再继续使用'})
        if disk.if_close:
            raise serializers.ValidationError({'detail': '你的网盘已关闭，先去开启再继续使用吧！'})
        folder_id = validated_data.get('folder_id')
        if folder_id:
            folder=Folder.objects.filter(id=folder_id)
            if not folder:
                raise serializers.ValidationError({'detail':'该该文件夹不存在！请重新选择'})
            else:
                folder=folder[0]
                if folder.if_delete:
                    raise serializers.ValidationError({'detail':'该文件夹已被回收，先去回收箱恢复吧'})
                if folder.disk!=disk:
                    raise serializers.ValidationError({'detail':'不能克隆到别人的文件夹下！'})
        file_from=validated_data.get('file_from')
        id_list=validated_data.get('id_list')
        if_open=validated_data.get('if_open')
        if len(id_list)>len(set(id_list)):
            raise serializers.ValidationError({'detail':'id列表不能重复！'})
        if id_list:
            if file_from=='open_file':
                for id in id_list:
                    file=File.objects.filter(id=id)
                    if file:
                        file=file[0]
                        if not file.if_open:
                            raise serializers.ValidationError({'detail':'该文件未开放！你不能克隆'})
                        if file.if_delete:
                            raise serializers.ValidationError({'detail':'被克隆文件已被回收，克隆终止！'})
                        if folder_id:
                            if folder.if_open:
                                if not if_open:
                                    raise serializers.ValidationError({'detail':'该文件夹已开放，设置当前克隆文件不开放无效！'})
                                else:
                                    fi=File.objects.create(name=file.name, folder_id=folder_id, file=file.file,extension=file.extension, size=file.size, disk=disk,if_open=True,if_auto_open=True,if_clone=True,clone_from=file,thumbnail=file.thumbnail)
                            else:
                                fi=File.objects.create(name=file.name, folder_id=folder_id, file=file.file,extension=file.extension, size=file.size, disk=disk, if_open=if_open, if_clone=True, clone_from=file,thumbnail=file.thumbnail)
                            folder.file_count+=1
                            folder.save()
                        else:
                            if disk.if_open:
                                if not if_open:
                                    raise serializers.ValidationError({'detail':'你的网盘已开放，设置当前克隆文件不开放无效！'})
                                else:
                                    fi=File.objects.create(name=file.name,file=file.file,extension=file.extension,size=file.size,disk=disk,if_open=True,if_auto_open=True,if_clone=True,clone_from=file,thumbnail=file.thumbnail)
                            else:
                                fi = File.objects.create(name=file.name, file=file.file,extension=file.extension, size=file.size, disk=disk,if_open=if_open, if_clone=True, clone_from=file,thumbnail=file.thumbnail)
                            disk.root_file_count+=1
                        labels=Label.objects.filter(my_file=file)
                        if labels:
                            for lab in labels:
                                fi.label.add(lab)
                        auto_labels=Label.objects.filter(my_auto_file=file)
                        if auto_labels:
                            for auto_lab in auto_labels:
                                fi.auto_label.add(auto_lab)
                        fi.save()
                        file.clone_count+=1
                        disk.file_count+=1
                        disk.save()
                        file.save()
                    else:
                        raise serializers.ValidationError({'detail':'文件夹id不存在！克隆终止'})
            elif file_from=='sharelink':
                for id in id_list:
                    sharelink_file=ShareLinkFile.objects.filter(id=id)
                    if sharelink_file:
                        sharelink_file=sharelink_file[0]
                        if sharelink_file.if_delete:
                            raise serializers.ValidationError({'detail':'该分享文件已被回收！不能克隆'})
                        checked=CheckedUser.objects.filter(user_id=user_id,if_disable=False,share_link=sharelink_file.sharelink)
                        if not checked:
                            raise serializers.ValidationError({'detail':'你没有通过该分享链接验证，先去找分享者获取链接和密码吧'})
                        else:
                            sharelink=sharelink_file.sharelink
                            if sharelink.time_limit == None:
                                pass
                            elif sharelink.time_limit > datetime.now():
                                pass
                            else:
                                raise serializers.ValidationError({'detail': '该分享链接已过期，你不能再克隆！'})
                            if folder_id:
                                if folder.if_open:
                                    if not if_open:
                                        raise serializers.ValidationError({'detail': '该文件夹已开放，设置当前克隆文件不开放无效！'})
                                    else:
                                        fi=File.objects.create(name=sharelink_file.name,folder_id=folder_id,file=sharelink_file.file,extension=sharelink_file.extension,size=sharelink_file.size,disk=disk,if_open=True,if_auto_open=True,if_clone=True,thumbnail=sharelink_file.thumbnail)
                                else:
                                    fi=File.objects.create(name=sharelink_file.name,folder_id=folder_id,file=sharelink_file.file,extension=sharelink_file.extension,size=sharelink_file.size,disk=disk,if_open=if_open,if_clone=True,thumbnail=sharelink_file.thumbnail)
                                folder.file_count+=1
                                folder.save()
                            else:
                                if disk.if_open:
                                    if not if_open:
                                        raise serializers.ValidationError({'detail':'该硬盘已公开，设置当前克隆文件不开放无效！'})
                                    else:
                                        fi = File.objects.create(name=sharelink_file.name,file=sharelink_file.file,extension=sharelink_file.extension,size=sharelink_file.size, disk=disk, if_open=True,if_auto_open=True, if_clone=True,thumbnail=sharelink_file.thumbnail)
                                else:
                                    fi = File.objects.create(name=sharelink_file.name,file=sharelink_file.file,extension=sharelink_file.extension,size=sharelink_file.size, disk=disk, if_open=if_open,if_clone=True, thumbnail=sharelink_file.thumbnail)
                                disk.root_file_count+=1
                        sharelink_file_labels=Label.objects.filter(sharelink_file=sharelink_file)
                        if sharelink_file_labels:
                            for sh_fi_lab in sharelink_file_labels:
                                fi.label.add(sh_fi_lab)
                        sharelink_file_auto_labels=Label.objects.filter(sharelink_auto_file=sharelink_file)
                        if sharelink_file_auto_labels:
                            for sh_fi_auto_lab in sharelink_file_auto_labels:
                                fi.auto_label.add(sh_fi_auto_lab)
                        fi.save()
                        disk.file_count+=1
                        disk.save()
                        sharelink_file.clone_count+=1
                        sharelink_file.save()
                        CheckedUserLog.objects.create(type='clone',checked_user=checked[0],sharelink_file=sharelink_file)

                    else:
                        raise serializers.ValidationError({'detail':'分享链接文件不存在！克隆终止'})
            return fi
        else:
            raise serializers.ValidationError({'detail':'文件id列表不能为空！'})

class FileNameUpdateSerializer(serializers.ModelSerializer):
    name=serializers.CharField(min_length=1,label='文件名',help_text='文件名',required=False)
    id=serializers.UUIDField(read_only=True)
    user_id=serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model=File
        fields=['name','id','user_id']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        disk = Disk.objects.filter(ower_id=user_id)
        disk = disk[0]
        if disk.if_disable:
            raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再继续使用'})
        if disk.if_close:
            raise serializers.ValidationError({'detail': '你的网盘已关闭，先去开启再继续使用吧！'})
        name=validated_data.get('name')
        if name:
            instance.name=name
            instance.save()
        return instance

class FileFolderUpdateSerializer(serializers.ModelSerializer):
    folder_id=serializers.UUIDField(required=False,label='文件夹id',help_text='文件夹id')
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id=serializers.UUIDField(read_only=True)
    class Meta:
        model=File
        fields=['folder_id','user_id','id']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        disk = Disk.objects.filter(ower_id=user_id)
        disk = disk[0]
        if disk.if_disable:
            raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再继续使用'})
        if disk.if_close:
            raise serializers.ValidationError({'detail': '你的网盘已关闭，先去开启再继续使用吧！'})
        folder_id = validated_data.get('folder_id')
        if folder_id:
            folder=Folder.objects.filter(id=folder_id,if_delete=False)
            if folder:
                folder=folder[0]
                if folder.disk==instance.disk:
                    files=File.objects.filter(name=instance.name,folder=folder)
                    if files:
                        raise serializers.ValidationError({'detail':'该文件夹存在同名文件！先修改文件名吧！'})
                    if folder.if_open:
                        instance.if_open=True
                        instance.if_auto_open=True
                    else:
                        if (instance.if_open) and (instance.if_auto_open==False):
                            pass
                        else:
                            instance.if_open = False
                            instance.if_auto_open = False
                    if instance.folder:
                        instance.folder.file_count-=1
                        instance.folder.save()
                    else:
                        disk.root_file_count-=1
                        disk.save()
                    instance.folder=folder
                    folder.file_count+=1
                    folder.save()
                else:
                    raise serializers.ValidationError({'detial':'你的文件不能挂在别人的文件夹下！'})
            else:
                raise serializers.ValidationError({'detail':'该文件夹不存在或已被回收！请检查并重新输入'})
        else:
            if instance.folder:
                instance.folder.file_count -= 1
                instance.folder.save()
            else:
                raise serializers.ValidationError({'detail':'当前文件所在位置未改变！请检查并重新输入'})
            instance.folder=None
        instance.save()
        return instance

class FileOpenSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id=serializers.UUIDField(read_only=True)
    class Meta:
        model=File
        fields=['if_open','user_id','id']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        disk = Disk.objects.filter(ower_id=user_id)
        disk = disk[0]
        if disk.if_disable:
            raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再继续使用'})
        if disk.if_close:
            raise serializers.ValidationError({'detail': '你的网盘已关闭，先去开启再继续使用吧！'})
        if_open=validated_data.get('if_open')
        if if_open:
            if instance.if_open:
                raise serializers.ValidationError({'detail':'未改变文件夹开放状态！请检查输入'})
            else:
                instance.if_open = if_open
        else:
            if instance.if_open:
                if instance.folder.if_open:
                    raise serializers.ValidationError({'detail':'当前文件所在文件夹已开放，设置当前文件不开放无效！'})
                else:
                    instance.if_open=False
            else:
                raise serializers.ValidationError({'detail':'未改变文件夹开放状态！请检查输入'})
        instance.save()
        return instance

class FileDeleteSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.UUIDField(read_only=True)
    class Meta:
        model=File
        fields=['if_delete','user_id','id']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        disk = Disk.objects.filter(ower_id=user_id)
        disk = disk[0]
        if disk.if_disable:
            raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再继续使用'})
        if disk.if_close:
            raise serializers.ValidationError({'detail': '你的网盘已关闭，先去开启再继续使用吧！'})
        if_delete=validated_data.get('if_delete')
        if if_delete!=instance.if_delete:
            if if_delete:
                instance.if_delete=True
                instance.delete_time=datetime.now()
            else:
                instance.if_delete=False
                instance.resume_time=datetime.now()
        else:
            raise serializers.ValidationError({'detail':'该文件回收状态未改变！请检查输入'})
        instance.save()
        return instance

def delete_folder_file(instance=None, new_list=None,count=0):
    list = []
    co=count
    if instance:
        if not instance.parent_folder:
            disk=instance.disk
            disk.root_folder_count-=1
            disk.save()
        else:
            parent_folder=instance.parent_folder
            parent_folder.child_folder_count-=1
            parent_folder.save()
        files = File.objects.filter(folder=instance)
        if files:
            for f in files:
                f.delete()
        folders = Folder.objects.filter(parent_folder=instance)
        if folders:
            for fo in folders:
                list.append(fo)
                co+=1
            return delete_folder_file(new_list=list,count=co)
        else:
            return None
    else:
        if new_list:
            for folder in new_list:
                files = File.objects.filter(folder=folder)
                if files:
                    for f in files:
                        f.delete()
                folders = Folder.objects.filter(parent_folder=instance)
                for fol in folders:
                    co+=1
                    list.append(fol)
            if list:
                return delete_folder_file(new_list=list,count=co)
            else:
                disk=instance.disk
                disk.folder_count-=co
                disk.save()
                return None
        else:
            return None

def sharelink_auto_folder_file(sharklink, new_list=None, folder=None):
    new_li = []
    if folder:
        files = File.objects.filter(folder=folder)
        if files:
            for f in files:
                sharklink.file.add(f)
                sharklink.auto_file.add(f)
        folders = Folder.objects.filter(parent_folder=folder)
        if folders:
            for fold in folders:
                sharklink.folder.add(fold)
                sharklink.auto_folder.add(fold)
                new_li.append(fold)
        else:
            return sharklink
        return sharelink_auto_folder_file(sharklink=sharklink, new_list=new_li)
    else:
        if new_list:
            for fold in new_list:
                folders = Folder.objects.filter(parent_folder=fold)
                if folders:
                    for fol in folders:
                        sharklink.folder.add(fol)
                        sharklink.auto_folder.add(fol)
                        new_li.append(fold)
                files = File.objects.filter(folder=fold)
                if files:
                    for f in files:
                        sharklink.file.add(f)
                        sharklink.auto_file.add(f)
            return sharelink_auto_folder_file(sharklink=sharklink, new_list=new_li)
        else:
            sharklink.save()
            return sharklink

def recursive_create_sharelink_folder(sharelink, folder=None, if_synchro=False, sh_fo_li=[]):
    sharelink_folder_list = []
    if folder:
        sharelink_folder = ShareLinkFolder.objects.create(original_folder=folder,name=folder.name, sharelink=sharelink)
        ShareLinkFolderPath.objects.create(sharelink_folder=sharelink_folder, path_folder_id=sharelink_folder.id,path_folder_name=folder.name)
        labels = Label.objects.filter(folder=folder)
        if labels:
            for lab in labels:
                sharelink_folder.label.add(lab)
        auto_labels = Label.objects.filter(my_auto_folder=folder)
        if auto_labels:
            for auto_lab in auto_labels:
                sharelink_folder.auto_label.add(auto_lab)
        sharelink_folder.save()
        sharelink_folder_list.append(sharelink_folder)
        return recursive_create_sharelink_folder(sharelink=sharelink, if_synchro=if_synchro,sh_fo_li=sharelink_folder_list)
    else:
        if sh_fo_li:
            for sh_fo in sh_fo_li:
                if not if_synchro:
                    sub_folders = Folder.objects.filter(parent_folder=sh_fo.original_folder, if_delete=False)
                    path = ShareLinkFolderPath.objects.filter(sharelink_folder=sh_fo).order_by('num')
                    parent_path_lenth = path.count()
                    if sub_folders:
                        sh_fo.child_sharelink_folder_count = sub_folders.count()
                        for child in sub_folders:
                            sharelink_folder = ShareLinkFolder.objects.create(original_folder=child,name=child.name, sharelink=sharelink,parent_sharelink_folder=sh_fo)
                            for p in path:
                                ShareLinkFolderPath.objects.create(sharelink_folder=sharelink_folder,path_folder_id=p.path_folder_id,path_folder_name=p.path_folder_name, num=p.num)
                            ShareLinkFolderPath.objects.create(num=parent_path_lenth + 1,sharelink_folder=sharelink_folder,path_folder_id=sharelink_folder.id,path_folder_name=child.name)
                            labels = Label.objects.filter(my_folder=child)
                            if labels:
                                for lab in labels:
                                    sharelink_folder.label.add(lab)
                            auto_labels = Label.objects.filter(my_auto_folder=folder)
                            if auto_labels:
                                for auto_lab in auto_labels:
                                    sharelink_folder.auto_label.add(auto_lab)
                            sharelink_folder.save()
                            sharelink_folder_list.append(sharelink_folder)
                    files = File.objects.filter(folder=sh_fo.original_folder, if_delete=False)
                    if files:
                        sh_fo.file_count = files.count()
                        sh_fo.save()
                        for fi in files:
                            sharelink_file = ShareLinkFile.objects.create(original_file=fi,name=fi.name, sharelink=sharelink,sharelink_folder=sh_fo, file=fi.file,extension=fi.extension, size=fi.size,thumbnail=fi.thumbnail)
                            labels = Label.objects.filter(my_file=fi)
                            if labels:
                                for lab in labels:
                                    sharelink_file.label.add(lab)
                            auto_labels = Label.objects.filter(my_auto_file=fi)
                            if auto_labels:
                                for auto_lab in auto_labels:
                                    sharelink_file.auto_label.add(auto_lab)
                            sharelink_file.save()
                else:
                    sub_folders = Folder.objects.filter(parent_folder=sh_fo.original_folder)
                    path = ShareLinkFolderPath.objects.filter(sharelink_folder=sh_fo).order_by('num')
                    parent_path_lenth = path.count()
                    if sub_folders:
                        sh_fo.child_sharelink_folder_count = sub_folders.filter(if_delete=False).count()
                        for child in sub_folders:
                            sharelink_folder = ShareLinkFolder.objects.create(name=child.name, sharelink=sharelink,parent_sharelink_folder=sh_fo,if_delete=child.if_delete)
                            for p in path:
                                ShareLinkFolderPath.objects.create(sharelink_folder=sharelink_folder,path_folder_id=p.path_folder_id,path_folder_name=p.path_folder_name, num=p.num)
                            ShareLinkFolderPath.objects.create(num=parent_path_lenth + 1,sharelink_folder=sharelink_folder,path_folder_id=sharelink_folder.id,path_folder_name=child.name)
                            labels = Label.objects.filter(my_folder=child)
                            if labels:
                                for lab in labels:
                                    sharelink_folder.label.add(lab)
                            auto_labels = Label.objects.filter(my_auto_folder=folder)
                            if auto_labels:
                                for auto_lab in auto_labels:
                                    sharelink_folder.auto_label.add(auto_lab)
                            sharelink_folder.save()
                            sharelink_folder_list.append(sharelink_folder)
                    files = File.objects.filter(folder=sh_fo.original_folder)
                    if files:
                        sh_fo.file_count = files.filter(if_delete=False).count()
                        sh_fo.save()
                        for fi in files:
                            sharelink_file = ShareLinkFile.objects.create(original_file=fi,name=fi.name, sharelink=sharelink,sharelink_folder=sh_fo, file=fi.file,extension=fi.extension, size=fi.size,thumbnail=fi.thumbnail,if_delete=fi.if_delete)
                            labels = Label.objects.filter(my_file=fi)
                            if labels:
                                for lab in labels:
                                    sharelink_file.label.add(lab)
                            auto_labels = Label.objects.filter(my_auto_file=fi)
                            if auto_labels:
                                for auto_lab in auto_labels:
                                    sharelink_file.auto_label.add(auto_lab)
                            sharelink_file.save()
                return recursive_create_sharelink_folder(sharelink=sharelink, if_synchro=if_synchro,sh_fo_li=sharelink_folder_list)
        else:
            return None

class ShareLinkListSerializer(serializers.ModelSerializer):
    # password=serializers.CharField()
    password = serializers.SerializerMethodField()
    def get_password(self, obj):
        return return_my_words(obj.password)
    class Meta:
        model=ShareLink
        fields='__all__'


class ShareLinkCreateSerializer(serializers.Serializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    folder_id_list = serializers.ListField(child=serializers.UUIDField(), required=False,label='文件夹id', help_text='文件夹id',write_only=True, allow_empty=True,allow_null=True)
    file_id_list = serializers.ListField(child=serializers.UUIDField(), required=False, label='文件id', help_text='文件id',write_only=True, allow_empty=True,allow_null=True)
    if_password = serializers.BooleanField(label='是否加密', help_text='是否加密', required=True,write_only=True)
    time_limit = serializers.DateTimeField(label='过期时间', help_text='过期时间', required=False,allow_null=True)
    # word = serializers.CharField(label='密码明文', help_text='密码明文', read_only=True)
    if_synchro = serializers.BooleanField(required=True, label='链接是否和硬盘同步更新', help_text='链接是否和硬盘同步更新')
    password=serializers.CharField(read_only=True)
    id=serializers.UUIDField(read_only=True)
    status=serializers.CharField(read_only=True)
    class Meta:
        model = ShareLink
        fields = ['user_id', 'folder_id_list', 'file_id_list', 'password', 'time_limit', 'if_synchro','if_password','id','status']

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        folder_id_list = validated_data.get('folder_id_list')
        file_id_list = validated_data.get('file_id_list')
        if_synchro = validated_data.get('if_synchro')
        sharelink = ShareLink(user_id=user_id, if_synchro=if_synchro)
        if not folder_id_list:
            if not file_id_list:
                raise serializers.ValidationError({'detail': '分享内容不能为空'})
        folder_list = []
        if folder_id_list:
            if len(folder_id_list) > len(set(folder_id_list)):
                raise serializers.ValidationError({'detail': '不能包含重复的文件夹id！'})
            for folder_id in folder_id_list:
                folder = Folder.objects.filter(id=folder_id, if_delete=False)
                if not folder:
                    raise serializers.ValidationError({'detail': '某个文件夹不存在或已回收！请检查并重新选择'})
                else:
                    folder = folder[0]
                    if folder.disk.ower_id != user_id:
                        raise serializers.ValidationError({'detail': '你不能分享别人的文件夹！'})
                    folder_list.append(folder)
        file_list = []
        if file_id_list:
            if len(file_id_list) > len(set(file_id_list)):
                raise serializers.ValidationError({'detail': '不能包含重复的文件id！'})
            for file_id in file_id_list:
                file = File.objects.filter(id=file_id, if_delete=False)
                if not file:
                    raise serializers.ValidationError({'detail': '某个文件不存在或已回收！请检查并重新选择'})
                else:
                    file = file[0]
                    if file.disk.ower_id != user_id:
                        raise serializers.ValidationError({'detail': '你不能分享别人的文件！'})
                    else:
                        file_list.append(file)
        if_password = validated_data.get('if_password')
        if if_password:
            word = make_sharelink_word(4)
            password = make_my_password(word)
            sharelink.password = password
        time_limit = validated_data.get('time_limit')
        if time_limit:
            sharelink.time_limit = time_limit
        sharelink.save()
        if folder_list:
            for folder in folder_list:
                try:
                    recursive_create_sharelink_folder(sharelink=sharelink,folder=folder,if_synchro=if_synchro)
                except:
                    sharelink.status='error'
                    sharelink.save()
                    raise serializers.ValidationError({'detail':'出现错误，创建终止'})
        if file_list:
            for file in file_list:
                ShareLinkFile.objects.create(original_file=file,name=file.name, sharelink=sharelink, file=file.file,extension=file.extension, size=file.size,thumbnail=file.thumbnail)
        if if_password:
            sharelink.password=word
        return sharelink

class SharelinkTimeLimitUpdateSerializer(serializers.ModelSerializer):
    time_limit = serializers.DateTimeField(label='过期时间', help_text='过期时间', required=True)
    id=serializers.UUIDField(read_only=True)
    class Meta:
        model=ShareLink
        fields=['time_limit','id']
    def update(self, instance, validated_data):
        time_limit=validated_data.get('time_limit')
        if time_limit>instance.create_time:
            instance.time_limit=time_limit
        else:
            raise serializers.ValidationError({'detail':'输入时间有误！请检查并重新输入'})
        instance.save()
        return instance

class SharelinkIfPasswordUpdateSerializer(serializers.ModelSerializer):
    if_password = serializers.BooleanField(label='是否加密', help_text='是否加密', required=True)
    id=serializers.UUIDField(read_only=True)
    class Meta:
        model=ShareLink
        fields=['if_password','id']
    def update(self, instance, validated_data):
        if_password=validated_data.get('if_password')
        if if_password:
            word = make_sharelink_word(4)
            password = make_my_password(word)
            instance.password=password
            instance.save()
            instance.password=word
        else:
            instance.password=None
            instance.save()
        return instance

class CheckedUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model=CheckedUser
        fields='__all__'

class CheckedUserCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    password=serializers.CharField(write_only=True,label='密码',help_text='密码',required=False)
    class Meta:
        model=CheckedUser
        fields=['user_id','share_link_id','password']
    def create(self, validated_data):
        user_id=validated_data.get('user_id')
        sharelink_id=validated_data.get('share_link_id')
        sharelink=ShareLink.objects.filter(id=sharelink_id)
        if sharelink:
            sharelink=sharelink[0]
            if sharelink.status=='normal':
                checked=CheckedUser.objects.filter(share_link=sharelink,user_id=user_id)
                if checked:
                    raise serializers.ValidationError({'detail':'你已经通过认证！无需再认证该链接'})
                else:
                    if sharelink.time_limit>datetime.now():
                        password = validated_data.get('password')
                        if sharelink.password:
                            p=make_my_password(password)
                            if sharelink.password==p:
                                checked_user=CheckedUser.objects.create(share_link=sharelink,user_id=user_id)
                            else:
                                raise serializers.ValidationError({'detail':'密码错误！请检查并重新输入'})
                        else:
                            if password:
                                raise serializers.ValidationError({'detail':'该链接无密码！你无需输入密码，可直接通过认证'})
                            else:
                                checked_user=CheckedUser.objects.create(share_link=sharelink, user_id=user_id)
                    else:
                        raise serializers.ValidationError({'detail':'该链接已过期！'})
            else:
                raise serializers.ValidationError({'detail':'该链接异常！'})
        else:
            raise serializers.ValidationError({'detail':'该链接不存在！'})
        return checked_user

class CheckedUserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model=CheckedUser
        fields=['if_disable']
    def update(self, instance, validated_data):
        if_disable=validated_data.get('if_disable')
        if instance.if_disable:
            if if_disable:
                raise serializers.ValidationError({'detail':'未改变禁用状态！请检查输入'})
            else:
                instance.if_disable=False
        else:
            if if_disable:
                instance.if_disable = False
            if if_disable:
                raise serializers.ValidationError({'detail':'未改变禁用状态！请检查输入'})
        instance.save()
        return instance

class DownloadFileSerializer(serializers.Serializer):
    download_from = serializers.ChoiceField(
        choices=(('open_folder', '开放文件'), ('sharelink', '分享链接文件'), ('own_file', '自己的文件'),('message','消息文件')),
        label='下载开放文件还是分享链接还是自己的文件', help_text='下载开放文件还是分享链接还是自己的文件', required=True,write_only=True)
    verbose_id = serializers.UUIDField(label='verbose_id', help_text='verbose_id', required=True,write_only=True)
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    def create(self, validated_data):
        download_from = validated_data.get('download_from')
        verbose_id=validated_data.get('verbose_id')
        user_id=validated_data.get('user_id')
        if download_from == 'open_folder':
            file=File.objects.filter(verbose_id=verbose_id,if_delete=False)
            if file:
                file=file[0]
                if file.if_open:
                    file_name=file.name
                    file=file.file
                    file_path=MEDIA_ROOT+file.name
                    # data=json.dumps({'file_name':file_name,'file_path':file_path})
                    return {'file_name':file_name,'file_path':file_path}
                else:
                    raise serializers.ValidationError({"detail":'该文件未开放,或输入下载来源不正确！请检查并重新输入'})
            else:
                raise serializers.ValidationError({'detail':'文件不存在或已被回收！'})
        elif download_from=='own_file':
            file=File.objects.filter(verbose_id=verbose_id,if_delete=False)
            if file:
                file=file[0]
                if file.disk.ower_id==user_id:
                    file_name = file.name
                    file = file.file
                    file_path = MEDIA_ROOT + file.name
                    # data = json.dumps({'file_name': file_name, 'file_path': file_path})
                    return {'file_name':file_name,'file_path':file_path}
                else:
                    raise serializers.ValidationError({'detail':'这不是你的文件，请检查并重新输入'})
            else:
                raise serializers.ValidationError({'detail': '文件不存在或已被回收！'})
        elif download_from=='sharelink':
            sharlink_file=ShareLinkFile.objects.filter(verbose_id=verbose_id,if_delete=False)
            if sharlink_file:
                sharlink_file=sharlink_file[0]
                sharelink = sharlink_file.sharelink
                if sharelink.time_limit>datetime.now():
                    checked=CheckedUser.objects.filter(share_link=sharelink,user_id=user_id)
                    if checked:
                        checked=checked[0]
                        if checked.if_disable:
                            raise serializers.ValidationError({'detail':'你已被分享者设为禁止，不能再继续下载文件！'})
                        file_name=sharlink_file.name
                        file=sharlink_file.file
                        file_path=MEDIA_ROOT+file.name
                        CheckedUserLog.objects.create(checked_user=checked, type='download',sharelink_file=sharlink_file)
                        # data = json.dumps({'file_name': file_name, 'file_path': file_path})
                        return {'file_name':file_name,'file_path':file_path}
                    else:
                        raise serializers.ValidationError({'detail':'你未通过该文件验证，不能下载该文件！先去找分享者获取链接和密码吧'})
                else:
                    raise serializers.ValidationError({'detail':'该分享链接已过期！不能再下载'})
            else:
                raise serializers.ValidationError({'detail':'文件不存在或已被回收！请检查并重新输入'})
        elif download_from=='message':
            message=Message.objects.filter(message_file__disk_file__verbose_id=verbose_id,sender_id=user_id)
            if message:
                file = File.objects.filter(verbose_id=verbose_id, if_delete=False)
                if file:
                    file = file[0]
                    file_name = file.name
                    file = file.file
                    file_path = MEDIA_ROOT + file.name
                    # data=json.dumps({'file_name':file_name,'file_path':file_path})
                    return {'file_name': file_name, 'file_path': file_path}
                else:
                    raise serializers.ValidationError({'detail': '文件不存在或已被回收！'})
            else:
                message=Message.objects.filter(message_file__disk_file__verbose_id=verbose_id,receiver_message__receiver_id=user_id)
                if message:
                    file = File.objects.filter(verbose_id=verbose_id, if_delete=False)
                    if file:
                        file = file[0]
                        file_name = file.name
                        file = file.file
                        file_path = MEDIA_ROOT + file.name
                        # data=json.dumps({'file_name':file_name,'file_path':file_path})
                        return {'file_name': file_name, 'file_path': file_path}
                    else:
                        raise serializers.ValidationError({'detail': '文件不存在或已被回收！'})
                else:
                    message=Message.objects.filter(message_file__disk_file__verbose_id=verbose_id,receiver_group__group_receiver_message__receiver_id=user_id)
                    if message:
                        file = File.objects.filter(verbose_id=verbose_id, if_delete=False)
                        if file:
                            file = file[0]
                            file_name = file.name
                            file = file.file
                            file_path = MEDIA_ROOT + file.name
                            # data=json.dumps({'file_name':file_name,'file_path':file_path})
                            return {'file_name': file_name, 'file_path': file_path}
                        else:
                            raise serializers.ValidationError({'detail': '文件不存在或已被回收！'})
                    else:
                        raise serializers.ValidationError({'detail':'你不是该消息接受者！没有权限下载该文件！'})







from django.db import models
import uuid
from datetime import datetime
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from users.models import UserProfile

class Disk(models.Model):
    ower=models.OneToOneField(UserProfile,verbose_name='用户',related_name='my_disk')
    size=models.FloatField(verbose_name='网盘容量(b)',default=100000000)
    used_size=models.FloatField(verbose_name='已用使用大小(b)',default=0.0)
    if_close=models.BooleanField(verbose_name='用户是否关闭',default=False)
    close_time=models.DateTimeField(blank=True,null=True,verbose_name='关闭时间')
    resume_time = models.DateTimeField(blank=True, null=True, verbose_name='恢复时间')
    if_disable=models.BooleanField(default=False,verbose_name='是否被禁用')
    if_open=models.BooleanField(verbose_name='是否全部公开',default=True)
    file_count=models.IntegerField(verbose_name='文件数',default=0,)
    folder_count=models.IntegerField(verbose_name='文件夹数',default=0)
    root_file_count=models.IntegerField(verbose_name='根目录文件数',default=0)
    root_folder_count=models.IntegerField(verbose_name='根目录文件夹数',default=0)
    create_time = models.DateTimeField(default=datetime.now, verbose_name='创建时间')
    update_time = models.DateTimeField(verbose_name='修改时间',auto_now=True)
    class Meta:
        verbose_name='网盘'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.ower.name

class Label(models.Model):
    name=models.CharField(max_length=20,verbose_name='标签名',default='',unique=True)
    create_time=models.DateTimeField(default=datetime.now,verbose_name='创建时间')
    create_user=models.ForeignKey(UserProfile,verbose_name='创建人',blank=True,null=True)
    folder_count=models.IntegerField(default=0,verbose_name='文件夹数')
    file_count=models.IntegerField(default=0,verbose_name='文件量')
    class Meta:
        verbose_name='标签'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.name


class Folder(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True, verbose_name='id')
    name=models.CharField(max_length=50,verbose_name='文件夹名',default='')
    label=models.ManyToManyField(Label,verbose_name='标签',blank=True,related_name='my_folder')
    auto_label=models.ManyToManyField(Label,verbose_name='自动添加的标签',blank=True,related_name='my_auto_folder')
    parent_folder=models.ForeignKey('self',blank=True,null=True,verbose_name='父文件夹',related_name='sub_folder',on_delete=models.CASCADE)
    create_time=models.DateTimeField(verbose_name='创建时间',default=datetime.now)
    update_time=models.DateTimeField(auto_now=True,verbose_name='修改时间')
    disk=models.ForeignKey(Disk,verbose_name='网盘',related_name='my_all_folder')
    child_folder_count = models.IntegerField(default=0, verbose_name='文件夹数')
    file_count = models.IntegerField(default=0, verbose_name='文件量')
    # folder_size=models.FloatField(default=0.0,verbose_name='文件夹文件大小(b)')
    # if_root=models.BooleanField(verbose_name='是否为根目录（网盘下的直系目录）',default=True)
    if_open = models.BooleanField(verbose_name='是否全部公开',default=False)
    if_auto_open = models.BooleanField(verbose_name='是否自动递归公开', default=False)
    if_delete=models.BooleanField(verbose_name='是否回收',default=False)
    if_auto_delete=models.BooleanField(verbose_name='是否自动递归回收',default=False)
    clone_time=models.IntegerField(verbose_name='被克隆次数',default=0)
    if_clone = models.BooleanField(default=False, verbose_name='是否克隆')
    if_auto_clone=models.BooleanField(default=False,verbose_name='是否自动递归克隆')
    click_count=models.IntegerField(default=0,verbose_name='点击量')
    clone_count=models.IntegerField(default=0,verbose_name='克隆量')
    if_auto_resume = models.BooleanField(verbose_name='是否自动递归恢复', default=False)
    clone_from = models.ForeignKey('self', verbose_name='克隆哪个', related_name='which_clone_me', blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True, verbose_name='删除时间')
    resume_time = models.DateTimeField(blank=True, null=True, verbose_name='恢复时间')
    class Meta:
        verbose_name='文件夹'
        verbose_name_plural=verbose_name
        unique_together=('name','parent_folder')
    def __str__(self):
        return self.name


class FileExtension(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True, verbose_name='id')
    name = models.CharField(max_length=20, verbose_name='拓展名',unique=True)
    type=models.CharField(max_length=20,verbose_name='类型')
    thumbnail = models.ImageField(default='thumbnail/default/other_default.png', verbose_name='缩略图')
    # file_count=models.IntegerField(verbose_name='文件量',default=0)
    create_time=models.DateTimeField(default=datetime.now,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='文件拓展名'
        verbose_name_plural=verbose_name
        # unique_together=('name',)
    def __str__(self):
        return self.name


class File(models.Model):
    id=models.UUIDField(default=uuid.uuid4(),primary_key=True,verbose_name='id')
    verbose_id=models.UUIDField(default=uuid.uuid4(),verbose_name='用于下载的id')
    file=models.FileField(upload_to='disk_uploads/%Y/%m/%d',verbose_name='文件')
    extension=models.ForeignKey(FileExtension,verbose_name='文件拓展名',blank=True,null=True)
    name=models.CharField(verbose_name='文件名',blank=True,null=True,max_length=50,help_text='文件名')
    size=models.FloatField(verbose_name='文件大小(b)',default=0.0)
    label = models.ManyToManyField(Label, verbose_name='标签', blank=True, related_name='my_file')
    auto_label = models.ManyToManyField(Label, verbose_name='自动添加的标签', blank=True, related_name='my_auto_file')
    folder=models.ForeignKey(Folder,verbose_name='所属文件夹',blank=True,null=True,related_name='file',on_delete=models.CASCADE)
    disk=models.ForeignKey(Disk,verbose_name='网盘',related_name='my_all_file')
    if_open=models.BooleanField(verbose_name='是否公开',default=False)
    if_auto_open=models.BooleanField(verbose_name='是否自动递归公开',default=False)
    # width_field=models.PositiveIntegerField(default=55,verbose_name='缩略图默认宽度')
    # height_field=models.PositiveIntegerField(default=45,verbose_name='缩略图默认高度')
    thumbnail=models.ImageField(default='thumbnail/default/other_default.png',verbose_name='缩略图')
    if_clone=models.BooleanField(default=False,verbose_name='是否克隆')
    if_auto_clone=models.BooleanField(default=False,verbose_name='是否自动递归克隆')
    clone_from=models.ForeignKey('self',verbose_name='克隆哪个',related_name='which_clone_me',blank=True,null=True)
    create_time = models.DateTimeField(verbose_name='创建时间',default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    if_delete = models.BooleanField(verbose_name='是否回收', default=False)
    clone_count=models.IntegerField(verbose_name='克隆量',default=0)
    download_count=models.IntegerField(verbose_name='下载量',default=0)
    if_auto_delete=models.BooleanField(verbose_name='是否自动递归回收 ',default=False)
    if_auto_resume=models.BooleanField(verbose_name='是否自动递归恢复',default=False)
    delete_time=models.DateTimeField(blank=True,null=True,verbose_name='删除时间')
    resume_time=models.DateTimeField(blank=True,null=True,verbose_name='恢复时间')
    class Meta:
        verbose_name='文件'
        verbose_name_plural=verbose_name
        unique_together = ('name', 'folder')
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.name:
            self.name=str(self.file).split('/')[-1]
        if not self.extension:
            try:
                ext=str(self.file).split('.')[-1]
                file_extension=FileExtension.objects.filter(name__iexact=ext)
                if file_extension:
                    self.extension=file_extension.first()
                else:
                    self.extension=FileExtension.objects.create(name=ext,type='其他')
            except:
                self.extension=FileExtension.objects.get(name='other')
        # if not self.size:
        #     self.size=self.file.size
        return super(File,self).save(*args, **kwargs)
    # def delete(self,*args, **kwargs):
    #     try:
    #         if self.which_clone_me:
    #             pass
    #         else:
    #             self.file.delete()
    #     except:
    #         self.file.delete()
    #     return super(File, self).delete(*args, **kwargs)


class FolderPath(models.Model):
    num=models.IntegerField(verbose_name='编号',default=1)
    folder=models.ForeignKey(Folder,verbose_name='哪个文件夹',related_name='path',on_delete=models.CASCADE)
    path_folder_id=models.UUIDField(verbose_name='路径文件夹id',blank=True,null=True)
    path_folder_name=models.CharField(max_length=50,verbose_name='路径文件夹名',default='')
    create_time=models.DateTimeField(default=datetime.now,verbose_name='创建时间')
    class Meta:
        verbose_name='文件夹、文件路径'
        verbose_name_plural=verbose_name
        unique_together=('num','folder')
        ordering=('num',)
    def __str__(self):
        return self.folder.name

@receiver(pre_delete, sender=File)
def file_delete(sender, instance, **kwargs):
    file=File.objects.filter(file=instance.file)
    sharelink_file=ShareLinkFile.objects.filter(file=instance.file)
    if file.count()>1:
        pass
    else:
        if sharelink_file:
            pass
        else:
            instance.file.delete(False)
    disk = instance.disk
    disk.file_count -= 1
    disk.size-=instance.size
    folder = instance.folder
    if folder:
        folder.file_count -= 1
        folder.save()
    else:
        disk.root_file_count-=1
    disk.save()

class ShareLink(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True,verbose_name='id')
    password=models.CharField(max_length=100,verbose_name='密码',blank=True,null=True)
    user=models.ForeignKey(UserProfile,verbose_name='分享者',related_name='my_sharelink')
    if_synchro=models.BooleanField(default=True,verbose_name='链接是否和硬盘同步更新')
    status=models.CharField(choices=(('normal','正常'),('error','异常')),max_length=6,default='normal',verbose_name='状态')
    time_limit=models.DateTimeField(blank=True,null=True,verbose_name='过期时间')
    create_time=models.DateTimeField(default=datetime.now,verbose_name='创建时间')
    class Meta:
        verbose_name='分享链接'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.user.name

class ShareLinkFolder(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True, verbose_name='id')
    name = models.CharField(max_length=50, verbose_name='文件夹名', default='')
    original_folder=models.ForeignKey(Folder,verbose_name='对应原文件夹',related_name='sharelink_folder',blank=True,null=True)
    label = models.ManyToManyField(Label, verbose_name='标签', blank=True, related_name='sharelink_folder')
    auto_label = models.ManyToManyField(Label, verbose_name='自动添加的标签', blank=True, related_name='sharelink_auto_folder')
    parent_sharelink_folder = models.ForeignKey('self', blank=True, null=True, verbose_name='父文件夹', related_name='sub_sharelink_folder',on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    sharelink = models.ForeignKey(ShareLink, verbose_name='分享链接', related_name='my_sharelink_folder',on_delete=models.CASCADE)
    child_sharelink_folder_count = models.IntegerField(default=0, verbose_name='文件夹数')
    if_delete=models.BooleanField(verbose_name='是否回收',default=False)
    file_count = models.IntegerField(default=0, verbose_name='文件量')
    clone_time = models.IntegerField(verbose_name='被克隆次数', default=0)
    click_count = models.IntegerField(default=0, verbose_name='点击量')
    clone_count = models.IntegerField(default=0, verbose_name='克隆量')
    delete_time = models.DateTimeField(blank=True, null=True, verbose_name='回收时间')
    resume_time = models.DateTimeField(blank=True, null=True, verbose_name='恢复时间')
    class Meta:
        verbose_name='分享链接文件夹'
        verbose_name_plural=verbose_name
        unique_together=('name','sharelink','parent_sharelink_folder')
    def __str__(self):
        return self.name


class ShareLinkFile(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True, verbose_name='id')
    verbose_id = models.UUIDField(default=uuid.uuid4(), verbose_name='用于下载的id')
    original_file=models.ForeignKey(File,verbose_name='对应原文件',related_name='sharelink_file',blank=True,null=True)
    file = models.FileField(upload_to='disk_uploads/%Y/%m/%d/', verbose_name='文件')
    extension = models.ForeignKey(FileExtension, verbose_name='文件拓展名', blank=True, null=True)
    name = models.CharField(verbose_name='文件名', blank=True, null=True, max_length=50, help_text='文件名')
    size = models.FloatField(verbose_name='文件大小(b)', default=0.0)
    label = models.ManyToManyField(Label, verbose_name='标签', blank=True, related_name='sharelink_file')
    auto_label = models.ManyToManyField(Label, verbose_name='自动添加的标签', blank=True, related_name='sharelink_auto_file')
    sharelink=models.ForeignKey(ShareLink,verbose_name='分享链接',related_name='my_sharelink_file',on_delete=models.CASCADE)
    sharelink_folder = models.ForeignKey(ShareLinkFolder, verbose_name='分享链接文件夹', blank=True, null=True, related_name='sharelink_file')
    thumbnail = models.ImageField(default='thumbnail/default/other_default.png', verbose_name='缩略图')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    if_delete = models.BooleanField(verbose_name='是否回收', default=False)
    clone_count = models.IntegerField(verbose_name='克隆量', default=0)
    download_count = models.IntegerField(verbose_name='下载量', default=0)
    delete_time = models.DateTimeField(blank=True, null=True, verbose_name='回收时间')
    resume_time = models.DateTimeField(blank=True, null=True, verbose_name='恢复时间')
    class Meta:
        verbose_name='分享链接文件'
        verbose_name_plural=verbose_name
        unique_together=('sharelink','sharelink_folder','name')
    def __str__(self):
        return self.name


class CheckedUser(models.Model):
    share_link=models.ForeignKey(ShareLink,verbose_name='分享链接',related_name='checked_user',on_delete=models.CASCADE)
    user=models.ForeignKey(UserProfile,verbose_name='用户',related_name='what_share_link_i_checked')
    if_disable=models.BooleanField(verbose_name='是否被禁用',default=False)
    check_time=models.DateTimeField(default=datetime.now,verbose_name='验证时间')
    class Meta:
        verbose_name='已确认用户'
        verbose_name_plural=verbose_name
        unique_together=('share_link','user')
    def __str__(self):
        return self.user.name


class CheckedUserLog(models.Model):
    type=models.CharField(choices=(('download','下载'),('clone','克隆')),max_length=8,verbose_name='日志类型',default='clone')
    checked_user=models.ForeignKey(CheckedUser,verbose_name='已确认用户',related_name='checked_user_log')
    sharelink_file=models.ForeignKey(ShareLinkFile,related_name='checked_user_log',verbose_name='分享链接文件',blank=True,null=True,on_delete=models.CASCADE)
    sharelink_folder=models.ForeignKey(ShareLinkFolder,related_name='checked_user_log',verbose_name='分享链接文件夹',blank=True,null=True,on_delete=models.CASCADE)
    create_time=models.DateTimeField(default=datetime.now,verbose_name='创建时间')
    class Meta:
        verbose_name='已确认用户使用日志'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.type


class ShareLinkFolderPath(models.Model):
    num=models.IntegerField(verbose_name='编号',default=1)
    sharelink_folder=models.ForeignKey(ShareLinkFolder,verbose_name='分享链接文件夹',related_name='my_path',on_delete=models.CASCADE)
    path_folder_id=models.UUIDField(verbose_name='路径文件夹id',blank=True,null=True)
    path_folder_name = models.CharField(max_length=50, verbose_name='路径文件夹名', default='')
    create_time = models.DateTimeField(default=datetime.now, verbose_name='创建时间')
    class Meta:
        verbose_name = '分享链接文件夹路径'
        verbose_name_plural = verbose_name
        unique_together=('num','sharelink_folder')
        ordering = ('num',)
    def __str__(self):
        return self.sharelink_folder.name


class OpenFolderPath(models.Model):
    num=models.IntegerField(verbose_name='编号',default=1)
    folder=models.ForeignKey(Folder,verbose_name='文件夹',related_name='open_path',on_delete=models.CASCADE)
    path_folder_id = models.IntegerField(verbose_name='路径文件夹id', blank=True, null=True)
    path_folder_name = models.CharField(max_length=50, verbose_name='路径文件夹名', default='')
    create_time = models.DateTimeField(default=datetime.now, verbose_name='创建时间')
    class Meta:
        verbose_name='开放文件夹路径'
        verbose_name_plural=verbose_name
        unique_together=('num','folder')
        ordering=('num',)
    def __str__(self):
        return self.folder.name




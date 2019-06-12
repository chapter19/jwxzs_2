from rest_framework import viewsets,mixins,response,status,filters,permissions
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.http import StreamingHttpResponse,FileResponse
from urllib import parse

from .models import Disk,Folder,FileExtension,File,ShareLink,Label,FolderPath,OpenFolderPath,ShareLinkFolderPath,CheckedUser,CheckedUserLog
from .serializers import DiskRetrieveSerializer,DiskCreateSerializer,DiskStatusSerializer,DiskOpenSerializer,\
    FolderListSerializer,FolderCreateSerializer,FolderParentFolderUpdateSerializer,FolderNameUpdateSerializer,FolderIfOpenUpdateSerializer,FolderIfDeleteSerializer,\
    FileExtensionListSerializer,FileExtensionTypeSerializer,\
    FileListSerializer,FileCreateSerializer,FileNameUpdateSerializer,FileFolderUpdateSerializer,FileOpenSerializer,\
    FolderCloneSerializer,FileCloneSerializer,\
    delete_folder_file,\
    ShareLinkCreateSerializer,SharelinkTimeLimitUpdateSerializer,SharelinkIfPasswordUpdateSerializer,ShareLinkListSerializer,\
    CheckedUserCreateSerializer,CheckedUserListSerializer,CheckedUserUpdateSerializer,\
    LabelListSerializer,LabelCreateSerializer,\
    FolderPathSerializer,OpenFolderPathSerializer,\
    DownloadFileSerializer
from .filters import FolderFilter,FileExtensionFilter,FileFilter,LabelFilter,FolderPathFilter,OpenFolderPathFilter,CheckedUserFilter

from users.views import DefaultPagination


class DiskView(mixins.RetrieveModelMixin,mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    read:
        用户网盘详情，加用户id访问
    create:
        初始化网盘
    '''
    permissions=(permissions.IsAuthenticated,)
    lookup_field = 'ower__id'
    def get_serializer_class(self):
        if self.action=='retrieve':
            return DiskRetrieveSerializer
        elif self.action=='create':
            return DiskCreateSerializer
    def get_queryset(self):
        if self.action=='retrieve':
            return Disk.objects.filter(Q(if_open=True)|Q(ower=self.request.user))
        else:
            return Disk.objects.filter(ower=self.request.user)

class DiskStatusView(mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    关闭或重新开启网盘
    '''
    permissions=(permissions.IsAuthenticated,)
    lookup_field = 'ower__id'
    serializer_class = DiskStatusSerializer
    def get_queryset(self):
        return Disk.objects.filter(ower=self.request.user)


class DiskOpenView(mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    开放或不开放网盘
    '''
    permissions=(permissions.IsAuthenticated,)
    lookup_field = 'ower__id'
    serializer_class = DiskOpenSerializer
    def get_queryset(self):
        return Disk.objects.filter(ower=self.request.user)

class FolderView(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    list:
        获取文件夹列表，根目录要加参数parent_folder_id=null，获取某一文件夹的子文件夹，加参数parent_folder_id={id}，获取未回收的文件夹要加if_delete=false，获取开放文件夹要加if_open=true&if_auto_open=false，获取自己的文件夹要加参数disk__ower_id={user id}
    create:
        创建文件夹
    update:
        修改文件夹名
    partial_update:
        部分更新文件夹名
    delete:
        删除文件夹
    '''
    pagination_class = DefaultPagination
    permissions = (permissions.IsAuthenticated,)
    def get_serializer_class(self):
        if self.action=='list':
            return FolderListSerializer
        elif self.action=='create':
            return FolderCreateSerializer
        else:
            return FolderNameUpdateSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = FolderFilter
    ordering_fields = ('create_time','update_time','delete_time','resume_time','name')
    def get_queryset(self):
        if self.action=='list':
            return Folder.objects.filter(Q(if_open=True)|Q(disk__ower=self.request.user))
        else:
            return Folder.objects.filter(disk__ower=self.request.user)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user=self.request.user
        if instance.disk.ower!=user:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        delete_folder_file(instance)
        instance.delete()

class FolderParentFolderUpdateView(mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    update:
        更新文件夹路径
    '''
    permissions=(permissions.IsAuthenticated,)
    serializer_class = FolderParentFolderUpdateSerializer
    def get_queryset(self):
        return Folder.objects.filter(disk__ower=self.request.user)

class FolderIfOpenUpdateView(mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    update:
        更新文件夹开放状态
    '''
    permissions=(permissions.IsAuthenticated,)
    serializer_class = FolderIfOpenUpdateSerializer
    def get_queryset(self):
        return Folder.objects.filter(disk__ower=self.request.user)

class FolderIfDeleteUpdateView(mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    update:
        更新文件夹回收状态
    '''
    permissions = (permissions.IsAuthenticated,)
    serializer_class = FolderIfDeleteSerializer
    def get_queryset(self):
        return Folder.objects.filter(disk__ower=self.request.user)


class FolderCloneView(mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    create:
        克隆文件夹
    '''
    permissions = (permissions.IsAuthenticated,)
    serializer_class = FolderCloneSerializer
    def get_queryset(self):
        return Folder.objects.filter(disk__ower=self.request.user)

class FileCloneView(mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    create:
        克隆文件夹
    '''
    permissions = (permissions.IsAuthenticated,)
    serializer_class = FileCloneSerializer
    def get_queryset(self):
        return File.objects.filter(disk__ower=self.request.user)

class FileExtensionView(mixins.ListModelMixin,mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        列出所有文件拓展名
    create:
        列出所有文件类型
    '''
    permissions = (permissions.IsAuthenticated,)
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = FileExtensionFilter
    ordering_fields = ('name',)
    def get_serializer_class(self):
        if self.action=='list':
            return FileExtensionListSerializer
        else:
            return FileExtensionTypeSerializer
    def perform_create(self, serializer):
        return serializer.save()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(data, status=status.HTTP_201_CREATED, headers=headers)
    queryset = FileExtension.objects.all()

class FileView(mixins.CreateModelMixin,mixins.ListModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    list:
        列出所有文件，加参数获取某一文件夹下的文件
    create:
        创建文件
    update:
        更新文件名
    partial_update:
        部分更新文件名
    delete:
        删除文件
    '''
    permissions = (permissions.IsAuthenticated,)
    pagination_class = DefaultPagination
    def get_serializer_class(self):
        if self.action=='list':
            return FileListSerializer
        elif self.action=='create':
            return FileCreateSerializer
        else:
            return FileNameUpdateSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = FileFilter
    ordering_fields = ('create_time', 'update_time', 'delete_time', 'resume_time', 'name')
    def get_queryset(self):
        base_query = File.objects.filter(disk__ower=self.request.user)
        if_root=self.request._request.GET.get('if_root')
        # if if_root:
        #     # query=base_query.filter(folder=None)
        #     query=File.objects.filter(disk__ower=self.request.user,folder__isnull=True)
        #     # return query
        #     return query
        return base_query
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user=self.request.user
        if user!=instance.disk.ower:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.file.delete()
        instance.delete()

class FileFolderUpdateView(mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    update:
        更新文件所属的文件夹
    '''
    permissions=(permissions.IsAuthenticated)
    serializer_class = FileFolderUpdateSerializer
    def get_queryset(self):
        return File.objects.filter(disk__ower=self.request.user)

class FileOpenView(mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    update:
        更改文件开放或不开放
    '''
    permissions=(permissions.IsAuthenticated,)
    serializer_class = FileOpenSerializer
    def get_queryset(self):
        return File.objects.filter(disk__ower_id=self.request.user)

class ShareLinkView(mixins.CreateModelMixin,mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    create:
        创建分享链接
    update:
        修改过期时间
    '''
    permissions = (permissions.IsAuthenticated,)
    def get_serializer_class(self):
        if self.action=='create':
            return ShareLinkCreateSerializer
        elif self.action=='list' or self.action=='retrieve':
            return ShareLinkListSerializer
        else:
            return SharelinkTimeLimitUpdateSerializer
    def get_queryset(self):
        return ShareLink.objects.filter(user=self.request.user)

class SharelinkPasswordUpdateView(mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    update:
        修改链接密码
    '''
    permissions = (permissions.IsAuthenticated,)
    serializer_class = SharelinkIfPasswordUpdateSerializer
    def get_queryset(self):
        return ShareLink.objects.filter(user=self.request.user)

class CheckedUserView(mixins.CreateModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    create:
        创建链接的用户认证
    retrieve:
        是否找到，是否通过验证
    '''
    permissions = (permissions.IsAuthenticated,)
    lookup_field = 'share_link'
    def get_serializer_class(self):
        if self.action=='create':
            return CheckedUserCreateSerializer
        elif self.action=='list' or (self.action=='retrieve'):
            return CheckedUserListSerializer
    def get_queryset(self):
        if self.action=='create' or 'retrieve':
            return CheckedUser.objects.filter(user=self.request.user)
    # filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    # filter_class = CheckedUserFilter

class CheckedUserUpdateView(mixins.UpdateModelMixin,viewsets.GenericViewSet,mixins.ListModelMixin):
    '''
    list:
        列出所有认证的用户
    update:
        更改认证用户的认证信息
    '''
    pagination_class = DefaultPagination
    permissions = (permissions.IsAuthenticated,)
    def get_serializer_class(self):
        if self.action == 'list':
            return CheckedUserListSerializer
        else:
            return CheckedUserUpdateSerializer
    def get_queryset(self):
        return CheckedUser.objects.filter(share_link__user=self.request.user)


class LabelView(mixins.ListModelMixin,mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        查询标签
    create：
        创建标签
    '''
    permissions = (permissions.IsAuthenticated,)
    def get_serializer_class(self):
        if self.action=='create':
            return LabelCreateSerializer
        elif self.action=='list':
            return LabelListSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = LabelFilter
    ordering_fields = ('create_time', 'name')
    def get_queryset(self):
        return Label.objects.all()

class FolderPathView(mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    list:
        查询文件夹路径
    '''
    permissions = (permissions.IsAuthenticated,)
    def get_queryset(self):
        return FolderPath.objects.filter(folder__disk__ower=self.request.user)
    serializer_class = FolderPathSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = FolderPathFilter
    # def list(self, request, *args, **kwargs):
    #     folder_id=request.GET.get('folder_id')
    #     if folder_id:
    #         folder=Folder.objects.filter(id=folder_id)
    #         if folder:
    #             folder=folder[0]
    #             folder.click_count+=1
    #             folder.save()
    #     return super(FolderPathView,self).list(request, *args, **kwargs)
    # ordering_fields = ('num',)

class OpenFolderPathView(mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    list:
        查询开放文件夹路径
    '''
    permissions = (permissions.IsAuthenticated,)
    def get_queryset(self):
        return OpenFolderPath.objects.all()
    serializer_class = OpenFolderPathSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = OpenFolderPathFilter
    def list(self, request, *args, **kwargs):
        folder_id=request.GET.get('folder_id')
        if folder_id:
            folder=Folder.objects.filter(id=folder_id)
            if folder:
                folder=folder[0]
                folder.click_count+=1
                folder.save()
        return super(OpenFolderPathView,self).list(request, *args, **kwargs)

    # ordering_fields = ('num',)

class DownloadFileView(mixins.CreateModelMixin,viewsets.GenericViewSet):
    permissions = (permissions.IsAuthenticated,)
    serializer_class = DownloadFileSerializer
    def perform_create(self, serializer):
        serializer.save()
    def file_iterator(self,file_name, chunk_size=512):
        # 文件读取迭代器
        try:
            with open(file_name, 'rb') as f:
                while True:
                    data = f.read(chunk_size)
                    if data:
                        yield data
                    else:
                        break
        except IOError as e:
            print('error，下载文件异常')
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data=serializer.instance
        file_data=self.file_iterator(file_name=data['file_path'])
        # res=FileResponse(open(data['file_path'], 'rb'))
        # res['Content-Type']='application/ecmascript'

        res=StreamingHttpResponse(file_data)
        res['Content-Type'] = 'application/octet-stream'
        sp=data['file_name'].split('.')
        file_name=parse.quote(sp[0],encoding='utf-8')+'.'+sp[-1]
        res['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
        return res
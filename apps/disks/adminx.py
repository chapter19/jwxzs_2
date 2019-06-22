#-*- coding:utf-8 -*-
import xadmin

from .models import Disk,Label,Folder,FileExtension,File,ShareLink,\
    ShareLinkFolder,ShareLinkFile,ShareLinkFolderPath,OpenFolderPath,\
    CheckedUser,CheckedUserLog

class DiskAdmin(object):
    model_icon='fa fa-cloud-download'
    list_display=['ower','size','used_size','if_close','close_time','resume_time','if_disable','file_count','folder_count','root_file_count','root_folder_count','if_open','id','create_time','update_time']
    search_fields=['ower__username','ower__name','my_all_folder__name']
    list_filter=['ower__username','ower__name','size','used_size','if_close','close_time','resume_time','if_disable','if_open','file_count','folder_count','root_file_count','root_folder_count','create_time','update_time']


class LabelAdmin(object):
    model_icon = 'fa fa-cloud-download'
    list_display=['name','create_time','create_user','folder_count','file_count']
    search_fields=['name','create_user__username','create_user__name']
    list_filter=['name','create_user__username','create_user__name','folder_count','file_count','create_time']

class FolderAdmin(object):
    model_icon = 'fa fa-cloud-download'
    list_display=['name','parent_folder','if_delete','if_auto_delete','create_time','update_time','disk','child_folder_count','file_count','if_open','if_auto_open','clone_time','if_clone','if_auto_clone','click_count','clone_count','if_auto_resume','id']
    search_fields=['name','parent_folder__name','disk__ower__name','disk__ower__username']
    list_filter=['name','create_time','update_time','disk__ower__username','disk__ower__name','parent_folder__name','parent_folder_id','auto_label','label','child_folder_count','file_count','if_auto_open','if_open','if_delete','if_auto_delete','clone_time','if_clone','if_auto_clone','click_count','clone_count','if_auto_resume','clone_from_id','delete_time','resume_time']


class FileExtensionAdmin(object):
    model_icon = 'fa fa-cloud-download'
    list_display=['name','type','thumbnail','create_time','update_time']
    search_fields=['name','type']
    list_filter=['name','type','create_time','update_time']


class FileAdmin(object):
    model_icon = 'fa fa-cloud-download'
    list_display=['name','verbose_id','file','extension','size','folder','disk','if_open','if_auto_open','thumbnail','if_clone','if_auto_clone','clone_from','create_time','update_time','if_delete','clone_count','download_count','if_auto_delete','if_auto_resume','delete_time','resume_time','id']
    search_fields=['name','extension__name','folder__name','disk__ower__name','disk__ower__username']
    list_filter=['name','label__name','extension','extension__type','folder__name','disk__ower__name','disk__ower__username','if_open','if_auto_open','if_clone','if_auto_clone','create_time','update_time','if_delete','clone_count','download_count','if_auto_delete','if_auto_resume','delete_time','resume_time']

class FolderPathAdmin(object):
    model_icon = 'fa fa-cloud-download'
    list_display=['folder','num','path_folder_id','path_folder_name','create_time','id']
    search_fields=['folder__name','folder__id','folder__disk__ower__username','folder__disk__ower__name']
    list_filter=['num','folder__name','folder__disk__ower__username','folder__disk__ower__name','path_folder_name','create_time']


class ShareLinkAdmin(object):
    model_icon = 'fa fa-cloud-download'
    list_display=['password', 'user', 'if_synchro','status','create_time','time_limit', 'id']
    search_fields=['password', 'user__name', 'user__username','id']
    list_filter=['password', 'if_synchro','user__name', 'user__username','status','time_limit','create_time']

class ShareLinkFolderAdmin(object):
    model_icon = 'fa fa-cloud-download'
    list_display=['name','original_folder','parent_sharelink_folder','create_time','update_time','sharelink','child_sharelink_folder_count','if_delete','file_count','clone_time','click_count','clone_count','delete_time','resume_time','id']
    search_fields=['name','parent_sharelink_folder__name','sharelink__user__username','sharelink__user__name','sharelink__password']
    list_filter=['name','parent_sharelink_folder__name','create_time','update_time','sharelink_id','sharelink__password','sharelink__user__username','sharelink__user__name','child_sharelink_folder_count','if_delete','file_count','clone_time','click_count','clone_count','delete_time','resume_time']

class ShareLinkFileAdmin(object):
    model_icon = 'fa fa-cloud-download'
    list_display=['name','extension','file','original_file','verbose_id','id','size','sharelink','sharelink_folder','thumbnail','create_time','update_time','if_delete','clone_count','download_count','delete_time','resume_time']
    search_fields=['id','name','sharelink__user__username','sharelink__user__name','sharelink__password']
    list_filter=['verbose_id','extension','name','size','sharelink__user__username','sharelink__user__name','sharelink__password','sharelink_folder__name','create_time','update_time','if_delete','clone_count','download_count','delete_time','resume_time']

class CheckedUserAdmin(object):
    model_icon = 'fa fa-cloud-download'
    list_display=['share_link','user','if_disable','check_time','id']
    search_fields=['share_link__user__username','share_link__user__name','share_link__password','id']
    list_filter=['user__username','user__name','share_link__user__username','share_link__user__name','share_link__password','share_link__status','share_link__time_limit']

class CheckedUserLogAdmin(object):
    model_icon = 'fa fa-cloud-download'
    list_display=['checked_user','type','sharelink_file','sharelink_folder','create_time']
    search_fields=['checked_user__user__username','checked_user__user__name','checked_user__share_link__user__username','checked_user__share_link__user__name','checked_user__share_link__password']
    list_filter=['type','checked_user__user__username','checked_user__user__name','checked_user__share_link__user__username','checked_user__share_link__user__name','checked_user__share_link__password','checked_user__share_link__status','checked_user__share_link__time_limit','checked_user__if_disable','sharelink_folder__name','sharelink_file__name']

class ShareLinkFolderPathAdmin(object):
    model_icon = 'fa fa-cloud-download'
    list_display=['sharelink_folder','num','path_folder_id','path_folder_name','create_time','id']
    search_fields=['path_folder_id','path_folder_name','sharelink_folder__name','sharelink_folder__id']
    list_filter=['num','sharelink_folder__name','path_folder_id','path_folder_name','create_time','sharelink_folder__sharelink__user__username','sharelink_folder__sharelink__user__name']

class OpenFolderPathAdmin(object):
    model_icon = 'fa fa-cloud-download'
    list_display=['folder','num','path_folder_id','path_folder_name','create_time','id']
    search_fields=['folder__name','folder__id','path_folder_id','path_folder_name']
    list_filter=['num','folder__name','path_folder_id','path_folder_name','create_time','folder__parent_folder__name']



xadmin.site.register(Disk, DiskAdmin)
xadmin.site.register(Label, LabelAdmin)
xadmin.site.register(Folder, FolderAdmin)
xadmin.site.register(FileExtension, FileExtensionAdmin)
xadmin.site.register(File, FileAdmin)
xadmin.site.register(ShareLink, ShareLinkAdmin)
xadmin.site.register(ShareLinkFolder, ShareLinkFolderAdmin)
xadmin.site.register(ShareLinkFile, ShareLinkFileAdmin)
xadmin.site.register(CheckedUser, CheckedUserAdmin)
xadmin.site.register(CheckedUserLog, CheckedUserLogAdmin)
xadmin.site.register(ShareLinkFolderPath, ShareLinkFolderPathAdmin)
xadmin.site.register(OpenFolderPath, OpenFolderPathAdmin)


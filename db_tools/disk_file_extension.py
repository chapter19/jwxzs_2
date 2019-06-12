#-*- coding:utf-8 -*-

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
django.setup()
import uuid

from disks.models import FileExtension


def create_file_extension():
    datas=[(('zip','zip'),('7z','7z'),('rar','rar'),('tar','tar'),('gz','gz'),('bzip','bzip'),('bz2','bz2'),('zix','zix'),('zipx','zipx'),('zz','zz'),('txz','txz')),
        (('png','png'),('jpg','jpg'),('jpeg','jpeg'),('gif','gif'),('svg','svg'),),
        (('doc','doc'),('docx','docx'),('pdf','pdf'),('txt','txt'),('md','md'),('caj','caj'),('log','log'),),
        (('xls','xls'),('xlsx','xlsx'),('csv','csv'),('numbers','numbers')),
        (('ppt','ppt'),('pptx','pptx'),('key','key'),('pps','pps')),
        (('mp3','mp3'),('wav','wav'),('wv','wv'),('tta','tta'),('m4a','m4a'),('cda','cda'),('aiff','aiff'),('aif','aif'),('midi','midi'),('mid','mid'),('wma','wma'),('ogg','ogg'),('amr','amr'),('ape','ape'),('fla','fla'),('flac','flac'),('acc','acc'),('swf','swf')),
        (('exe','exe'),('jar','jar'),('apk','apk'),('app','app'),('dmg','dmg'),('pkg','pkg'),),
        (('mp4','mp4'),('flv','flv'),('avi','avi'),('mkv','mkv'),('mov','mov'),('mpeg','mpeg'),('mpg','mpg'),('dat','dat'),('asf','asf'),('wmv','wmv'),('3gp','3gp'),('navi','navi'),('f4v','f4v'),('qsv','qsv'),('rm','rm'),('rmvb','rmvb'),),
        (('py','py'),('ipython','ipython'),('ipynb','ipynb'),('pyc','pyc'),('h','h'),('cpp','cpp'),('c','c'),('java','java'),('jsp','jsp'),('class','class'),('php','php'),('html','html'),('htm','htm'),('xml','xml'),('css','css'),('js','js'),('swift','swift'),('asp','asp'),('aspx','aspx'),('ascx','ascx'),('cs','cs'),('sh','sh'),('d','d'),('in','in'),('am','am'),('sped','sped'),('sub','sub'),('sql','sql'),('bat','bat'),('go','go')),
        (('json', 'json'),('db','db'),('sqlit3','sqlit3'),('mdf','mdf'),('mdb','mdb'),('dbf','dbf'),('wdb','wdb')),
        (('woff','woff'),('woff2','woff2'),('ttf','ttf'),('otf','otf'),('eot','eof')),
        (('rt','rt'),('ass','ass'),('ssa','ssa'),('smi','smi'),('ssf','ssf'),('lrc','lrc'),('srt','srt')),
        (('torrent','torrent'),),
        (('other','other'),),
        ]

    list=[('', '压缩包'),
            ('','图片'),
            ('','文档'),
            ('','表格'),
            ('', '幻灯片'),
            ('','音频'),
            ('','应用程序'),
            ('','视频'),
            ('','代码脚本'),
            ('','数据文件'),
            ('','字体'),
            ('','字幕'),
            ('','种子'),
            ('','其他'),
          ]
    for d,li in zip(datas,list):
        for dd in d:
            try:
                file_extension=FileExtension.objects.filter(name=dd[0])
                if file_extension:
                    print(dd[0],li[1],'重复重复')
                else:
                    FileExtension.objects.create(id=uuid.uuid4(),name=dd[0],type=li[1])
            except:
                print('插入异常')

if __name__ == '__main__':
    create_file_extension()
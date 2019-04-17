#### 一、安装tesseract
#### 二、安装依赖包如下

backports.csv==1.0.7<br>
beautifulsoup4==4.7.1<br>
bs4==0.0.1<br>
certifi==2019.3.9<br>
chardet==3.0.4<br>
coreapi==2.3.3<br>
coreschema==0.0.4<br>
defusedxml==0.5.0<br>
diff-match-patch==20181111<br>
Django==1.11.6<br>
django-cors-headers==2.5.2<br>
django-crispy-forms==1.7.2<br>
django-filter==2.1.0<br>
django-formtools==2.1<br>
django-guardian==1.5.0<br>
django-import-export==1.2.0<br>
djangorestframework==3.9.2<br>
djangorestframework-jwt==1.11.0<br>
et-xmlfile==1.0.1<br>
future==0.17.1<br>
html5lib==1.0.1<br>
httplib2==0.12.1<br>
idna==2.8<br>
itypes==1.1.0<br>
jdcal==1.4<br>
Jinja2==2.10<br>
lxml==4.3.3<br>
Markdown==3.1<br>
MarkupSafe==1.1.1<br>
mysqlclient==1.4.2.post1<br>
odfpy==1.4.0<br>
openpyxl==2.6.1<br>
Pillow==5.4.1<br>
PyJWT==1.7.1<br>
pymongo==3.7.2<br>
pytesseract==0.2.6<br>
pytz==2018.9<br>
PyYAML==5.1<br>
requests==2.21.0<br>
six==1.12.0<br>
soupsieve==1.9<br>
tablib==0.13.0<br>
uritemplate==3.0.0<br>
urllib3==1.24.1<br>
webencodings==0.5.1<br>
xlrd==1.2.0<br>
xlwt==1.3.0<br>
#### 三、修改数据库
找到/jwxzs_2/jwxzs_2/settings.py中DATABASES，修改数据库及密码<br>
#### 四、迁移数据库
python manage.py makemigrations<br>
python manage.py migrate




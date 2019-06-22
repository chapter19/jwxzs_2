import requests
from bs4 import BeautifulSoup
import time


class SpiderStaticTeacher:
    def __init__(self,id='201626703079',password='m19980220'):
        self.id=id
        self.password=password
        self.__s=requests.Session()

    # get方法请求，获得隐藏参数 viewstate、eventvalidation
    def __get_hid_data(self, url, error_time_limit=5,timeout=2):
        try:
            b = self.__s.get(url, timeout=timeout)
            soup = BeautifulSoup(b.text, 'html5lib')
            __VIEWSTATE = soup.select('input[id="__VIEWSTATE"]')
            __EVENTVALIDATION = soup.select('input[id="__EVENTVALIDATION"]')
            return __VIEWSTATE[0].get('value'), __EVENTVALIDATION[0].get('value')
        except:
            error_time_limit -= 1
            if error_time_limit > 0:
                print('__get_hid_data timeout, retrying。。')
                return self.__get_hid_data(url=url, error_time_limit=error_time_limit)
            else:
                return 0

    def sign_in(self,limit_time=10,timeout=5):
        try:
            url = 'http://jwc.jxnu.edu.cn/Portal/LoginAccount.aspx?t=account'
            data = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': '/wEPDwUJNjA5MzAzMTcwD2QWAmYPZBYCAgMPZBYGZg8WAh4EVGV4dAUgMjAxOeW5tDTmnIgxM+aXpSDmmJ/mnJ/lha0mbmJzcDtkAgIPZBYCAgEPFgIfAAUS6LSm5Y+35a+G56CB55m75b2VZAIDD2QWBAIBDw8WAh4HVmlzaWJsZWdkFgoCAQ8QZGQWAWZkAgMPZBYCAgEPFgIfAAUG5a2m5Y+3ZAIFDw8WAh8BaGQWAgIBDxAPFgYeDURhdGFUZXh0RmllbGQFDOWNleS9jeWQjeensB4ORGF0YVZhbHVlRmllbGQFCeWNleS9jeWPtx4LXyFEYXRhQm91bmRnZBAVGxLotKLmlL/ph5Hono3lrabpmaIS5Z+O5biC5bu66K6+5a2m6ZmiEuWIneetieaVmeiCsuWtpumZohXlnLDnkIbkuI7njq/looPlrabpmaIS5YWs6LS55biI6IyD55Sf6ZmiEuWbvemZheaVmeiCsuWtpumZohLljJblrabljJblt6XlrabpmaIb6K6h566X5py65L+h5oGv5bel56iL5a2m6ZmiEue7p+e7reaVmeiCsuWtpumZogzmlZnogrLlrabpmaIe5Yab5LqL5pWZ56CU6YOo77yI5q2m6KOF6YOo77yJEuenkeWtpuaKgOacr+WtpumZohvljoblj7LmlofljJbkuI7ml4XmuLjlrabpmaIV6ams5YWL5oCd5Li75LmJ5a2m6ZmiDOe+juacr+WtpumZogzova/ku7blrabpmaIJ5ZWG5a2m6ZmiEueUn+WRveenkeWtpuWtpumZohvmlbDlrabkuI7kv6Hmga/np5HlrablrabpmaIM5L2T6IKy5a2m6ZmiD+WkluWbveivreWtpumZognmloflrabpmaIb54mp55CG5LiO6YCa5L+h55S15a2Q5a2m6ZmiDOW/g+eQhuWtpumZohXmlrDpl7vkuI7kvKDmkq3lrabpmaIM6Z+z5LmQ5a2m6ZmiDOaUv+azleWtpumZohUbCDY4MDAwICAgCDYzMDAwICAgCDgyMDAwICAgCDQ4MDAwICAgCDU3MDAwICAgCDY5MDAwICAgCDYxMDAwICAgCDYyMDAwICAgCDQ1MCAgICAgCDUwMDAwICAgCDM3MDAwICAgCDgxMDAwICAgCDU4MDAwICAgCDQ2MDAwICAgCDY1MDAwICAgCDY3MDAwICAgCDU0MDAwICAgCDY2MDAwICAgCDU1MDAwICAgCDU2MDAwICAgCDUyMDAwICAgCDUxMDAwICAgCDYwMDAwICAgCDQ5MDAwICAgCDY0MDAwICAgCDUzMDAwICAgCDU5MDAwICAgFCsDG2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZxYBZmQCCw8PFgIeCEltYWdlVXJsBSRjaGVja2NvZGUuYXNweD9jb2RlPUEwRDM0OTkyRTY0QTA4QTlkZAINDxYCHwAFEEEwRDM0OTkyRTY0QTA4QTlkAgMPDxYCHwFoZGRkVKkChFZpdlQPdlHy2JNRlch/myJywKCzK0eOTM5tgKI=',
                '__EVENTVALIDATION': '/wEWCgL+uuD+AgKFsp/HCgL+44ewDwKiwZ6GAgKWuv6KDwLj3Z22BgL6up5fAv/WopgDAqbyykwC68zH9gaIVcuoN2ppvvS2+yQJvvk3Fl/uM/vu9jcD1EIn80deUg==',
                '_ctl0:cphContent:ddlUserType': 'Student',
                '_ctl0:cphContent:txtUserNum': self.id,
                '_ctl0:cphContent:txtPassword': self.password,
                '_ctl0:cphContent:txtCheckCode': 'YUN3',
                '_ctl0:cphContent:btnLogin': '登录'
            }
            wb_data = self.__s.post(url=url, data=data, timeout=timeout)
            soup = BeautifulSoup(wb_data.text, 'html5lib')
            jwtz = soup.select('#jwtz')
            if jwtz != []:
                print('sign in successfluly!')
                return True
            else:
                limit_t = limit_time - 1
                print('sign in fail')
                if limit_t > 0:
                    time.sleep(1)
                    print('sign_in failed, retrying。。')
                    return self.sign_in(limit_time=limit_t, timeout=timeout)
                else:
                    return None
        except:
            limit_ti = limit_time - 1
            if limit_ti > 0:
                print('sign_in timeout, retrying。。')
                return self.sign_in(limit_time=limit_ti, timeout=timeout)
            else:
                print(self.id)
                print(self.password)
                return None

    def testss(self):
        try:
            url=r'http://jwc.jxnu.edu.cn/MyControl/All_Display.aspx?UserControl=Xfz_Class_student2.ascx&bjh=2468045&kch=062301&xq=2016/9/1'
            wb_data=self.__s.get(url)
            soup1 = BeautifulSoup(wb_data.text, 'html5lib')
            stu_ids = soup1.select('tr[bgcolor="White"] > td:nth-of-type(3)')
            print(soup1)
            print(stu_ids)
            # for stu_id in stu_ids:
            #     sid=stu_id.get_text().strip()
            #     # print(sid)
            #     self.schedule_lesson_create_score(log_id=log_id,schlesson=schlesson,student_id=sid)
        except:
            pass

if __name__ == '__main__':
    sp=SpiderStaticTeacher()
    sp.sign_in()
    sp.testss()
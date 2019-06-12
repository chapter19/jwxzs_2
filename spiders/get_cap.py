#-*- coding:utf-8 -*-
# import cv2

import requests
from bs4 import BeautifulSoup
from PIL import Image
import os
# import numpy as np

def get_captcha(timeout=3,limit_time=5):
    try:
        url='http://jwc.jxnu.edu.cn/Portal/LoginAccount.aspx?t=account'
        wb_data=requests.get(url,timeout=timeout)
        soup=BeautifulSoup(wb_data.text,'lxml')
        id=soup.select('#_ctl0_cphContent_imgPasscode')[0]
        id=id.get('src')
        code_src='http://jwc.jxnu.edu.cn/Portal/'+id
        print(code_src)
        return code_src,id
    except:
        limit_time-=1
        if limit_time>=0:
            return get_captcha(limit_time=limit_time)
        else:
            return None


def download_img(timeout=3,limit_time=5):
    cap=get_captcha()
    if cap:
        try:
            img_data=requests.get(cap[0],timeout=timeout)
            src='./imgs/'+cap[1]+'.png'
            with open(src,'wb') as photo:
                photo.write(img_data.content)
                photo.close()
            return src
        except:
            limit_time -= 1
            if limit_time >= 0:
                return download_img(limit_time=limit_time)
            else:
                return None
    else:
        return None

def clean_captcha(timeout=3,limit_time=5):
    img_src=download_img()
    if img_src:
        try:
            image=Image.open(img_src)
            x, y = image.size
            p = Image.new('RGB', image.size, (255, 255, 255))
            p.paste(image, (0, 0, x, y), image)
            image = p.convert('L')
            os.remove(img_src)
            img_src='./imgs/'+img_src.split('=')[1].split('.')[0]+'.jpg'
            image.save(img_src)
            return image
            # image.show()
        except:
            limit_time -= 1
            if limit_time >= 0:
                return clean_captcha(limit_time=limit_time)
            else:
                return None
    else:
        return None

# def test():
#     img=cv2.imread('./0B2EF3BEC77B8DB3.jpg',1)
#     data=np.array(img)
#     print(data)




if __name__ == '__main__':
    # get_captcha()
    for i in range(10000):
        clean_captcha()
    # test()






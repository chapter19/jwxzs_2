#-*- coding:utf-8 -*-


# import os,django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
# django.setup()

from Crypto.Cipher import AES
import Crypto.Random
import base64
import binascii
from jwxzs_2.settings import AES_KEY



def auto_fill(x):
    if len(x) <= 32:
        # if
        return x.ljust(32).encode()
        # while len(x) not in [16, 24, 32]:
        #     x += " "
        #     return x.encode()
    else:
        raise("密钥长度不能大于32位！")

x=auto_fill(AES_KEY)
# print(x)

x=AES.new(x,AES.MODE_ECB)


def make_my_password(word,the_key=x):
    password=base64.encodebytes(the_key.encrypt(auto_fill(word)))
    return password


def return_my_words(password,the_key=x):
    # pa=bytes(password,encoding='utf-8')
    if type(password)==str:
        pa=password.encode(encoding='utf-8')
    else:
        pa=password
    word=the_key.decrypt(base64.decodebytes(pa)).strip().decode()
    return word







if __name__ == '__main__':
    password=make_my_password('A39t')
    print(password)
    # password=make_my_password('m19980220')
    # print(password)
    # word=return_my_words('tXZtl1UiccBjW7xZn/8D/p5Tm89hKCmsn//g0rW0c84=')
    # print(word)





#-*- coding:utf-8 -*-

import random

from utils.aes import make_my_password,return_my_words

def make_sharelink_word(len=4):
    seeds = 'avdefghijnqrtyABDEFGHJLNQRTY23456789'
    word=''
    for i in range(len):
        char=random.choice(seeds)
        word+=char
    return word
        # word+=char
    # password=make_my_password(word)
    # return word,password

if __name__ == '__main__':
    a=make_sharelink_word()
    print(a)
    # print(a)


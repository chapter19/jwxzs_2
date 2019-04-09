#-*- coding:utf-8 -*-
import pytesseract
# import tesserocr
from PIL import Image


img=Image.open('test4.png')
print(pytesseract.image_to_string(img))
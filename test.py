#coding:utf-8
from crawler import *
result = get_words()
english = result.split('\n')[0]
chinese = result.split('\n')[1]
author = result.split('\n')[2]
print(chinese,english,author)

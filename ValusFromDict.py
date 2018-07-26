#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf-8 -*-

import itertools

Dict={}


def getvalues(key):
    length = len(key)
    global Dict
    if length <= 0 :
        return True
    if length == 1 :
        if Dict.has_key(key):
            return True, Dict[key]
        else:
            return False
    result=[]
    for i in range (1, length):
        str1 = key[:i]
        if Dict.has_key(str1):
            x,y = getvalues(key[i:])
            if x:
                result = result + list(itertools.product(Dict[str1],y))

    if len(result) != 0:
        return True, result
    else:
        return False



global Dict
Dict = input("Dic=======")
#Dict={'1':['A','B','C'],'2':['D','E'],'12':['X'],'3':['P','Q']}
#Key = '123'
Key = input("Key========")
x, y = getvalues(Key)

if x:
    for value in y:
        print (str(value))
else:
    print 'No value for this key.'

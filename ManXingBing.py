#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf-8 -*-

import random
from BeautifulSoup import BeautifulSoup
import urllib
import urllib2
import sys
import socket
import MySQLdb

headers = [
    {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},
    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},
    {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},
    {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'},
    {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'}
]

MXB_Url = "http://jbk.39.net/zq/manxingbing/zl/?p=%d"


def getDiseases(URLs):
    for DiseaseUrl in URLs:
        req = urllib2.Request(DiseaseUrl, "", random.choice(headers))
        page_code = urllib2.urlopen(req)
        page_text = page_code.read()
        soup = BeautifulSoup(page_text)
        disease = {}
        item = soup.find(attrs={'class': 'intro'})
        # name = item.dt.text.encode("latin1").decode("gbk")
        disease['name'] = item.dt.text.encode("latin1").decode("gbk")
        #name = item.dt.text.encode("latin1").decode("gbk")
        details = soup.find(attrs={'class': 'info'})
        for item in details.findAll('li'):
            key = item.i.text.encode("latin1").decode("gbk")
            content = item.text.encode("latin1").decode("gbk")
            value = content[len(key):]
            disease[key]=value

for pageNum in range(1, 500):
    page_url = MXB_Url % pageNum
    req = urllib2.Request(page_url, "", random.choice(headers))
    page_code = urllib2.urlopen(req)
    page_text = page_code.read()
    soup = BeautifulSoup(page_text)
    deseases = []
    for item in soup.findAll(attrs={'class': 'drug-info-name'}):
        deseases.append(item.next.get('href'))
       #content = text.text.encode("latin1").decode("gbk")

    if len(deseases) == 0:
        break
    getDiseases(deseases)

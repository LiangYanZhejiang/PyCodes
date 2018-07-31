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
import chardet

reload(sys)
sys.setdefaultencoding("utf-8")

headers = [
    {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},
    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},
    {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},
    {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'},
    {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'}
]

MXB_Url = "http://jbk.39.net/zq/manxingbing/zl/?p=%d"
column_name = {u'别名：':'disease_alias',
               u'是否属于医保：':'medicare',
               u'发病部位：':'pathogenic_site',
               u'挂号的科室：':'departmant',
               u'传染性：':'infectivity',
               u'治疗方法：':'therapies',
               u'治愈率：':'cure_rate',
               u'治疗周期：':'treatment_cycle',
               u'多发人群：':'susceptible',
               u'治疗费用：':'cost',
               u'典型症状：':'symptom',
               u'临床检查：':'examination',
               u'并发症：':'syndrome',
               u'常用药品：':'drug',}


def getDiseases(URLs):
    for DiseaseUrl in URLs:
        req = urllib2.Request(DiseaseUrl, "", random.choice(headers))
        page_code = urllib2.urlopen(req)
        page_text = page_code.read()
        soup = BeautifulSoup(page_text)
        disease = {}
        item = soup.find(attrs={'class': 'intro'})
        # name = item.dt.text.encode("latin1").decode("gbk")
        try:
            disease['disease_name'] = item.dt.text.encode("latin1").decode("gbk","ignore")
        except:
            disease['disease_name'] = item.dt.text

        #name = item.dt.text.encode("latin1").decode("gbk")
        details = soup.find(attrs={'class': 'info'})
        for item in details.findAll('li'):
            try:
                key = item.i.text.encode("latin1").decode("gbk","ignore")
                content = item.text.encode("latin1").decode("gbk","ignore")
            except:
                key = item.i.text
                content = item.text
            value = content[len(key):]
            if column_name.has_key(key):
                disease[column_name[key]]=value

        insertData(disease)

def insertData(disease):
    global db
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 插入语句
    sql = """INSERT INTO manxingbing_tbl( """
    values = "VALUES("
    first = True

    for item in disease.iterkeys():
        if not first:
            sql = sql + ','
            values = values + ','
        sql = sql + item;
        values = values+"'"+disease[item]+"'"
        first =  False;

    sql = sql + ')'+ values + ');'

    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()


db = MySQLdb.connect("localhost", "root", "mysql", "manxingbing", charset='utf8')
for pageNum in range(1, 500):#end page 242
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
db.close()

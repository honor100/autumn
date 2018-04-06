#!/bin/env python3
# -*- coding: UTF-8 -*-

# File Name: util.py
# Author: liuyunsong
# Mail: liuyunsong@xxx.cn
# Created Time: Sat 08 Apr 2017 04:38:31 PM CST


import re
import sys
import json
import decimal
import datetime
import hashlib
import pymysql


def WARNING(*objs):
    print("WARNING:", *objs, file=sys.stderr)


class CommonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if isinstance(o, datetime.date):
            return o.isoformat()
        if isinstance(o, datetime.time):
            return o.isoformat()
        if isinstance(o, decimal.Decimal):
            return str(o)
        return json.JSONEncoder.default(self, o)
# 使用方法： json.dumps(yourobj, cls=CommonEncoder)


def formatSQL(sql):
    try:
        sarr = sql.lower().split("'")
        sarr[1::2] = ['?' for x in sarr[1::2]]
        _sql = "'".join(sarr)
        return re.sub(r"\b\d+\b", "?", _sql)
    except:
        return ""


# 加密后生成md5值，适用存储在数据库做密码比对
def md5(text):
    _text = text.encode('utf-8')
    return hashlib.md5(_text).hexdigest()


# 加密后生成sha1值，适用存储在数据库做密码比对
def sha1(text):
    _text = text.encode('utf-8')
    return hashlib.sha1(_text).hexdigest()


def escape_string(text):
    try:
        return pymysql.escape_string(text)
    except Exception as e:
        WARNING(e)
        return str(text)

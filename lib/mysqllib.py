#!/bin/env python3
# -*- coding: UTF-8 -*-

# File Name: lib/mysqllib.py
# Author: liuyunsong
# Mail: liuyunsong@xxx.cn
# Created Time: Sun 09 Apr 2017 01:35:39 PM CST


import sys
import pymysql
from .util import WARNING




def returnResult(res, desc = ""):
    return {"status": res, "reason": desc}
def returnStatus(result):
    return result["status"]
def returnReason(result):
    return result["reason"]

def decoupleResult(res):
    return returnStatus(res), returnReason(res)


class MysqlBase(object):
    def __init__(self, host=None, port=None, user='', passwd='', db='', charset="utf8mb4", connect_timeout=10, retry=3,
        use_unicode=1, unix_socket = None):
        if host is None and unix_socket is None:
            WARNING("Please specify a login method(by host or by socket)")
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__dbname = db
        self.__connect_timeout = connect_timeout
        self.__charset = charset
        self.__use_unicode = use_unicode
        self.__unix_socket = unix_socket

        self.retry = retry
        #self.cursor = None
        self.db = None
        self.lastrowid = 0

        self.__dictType = False

## MysqlBase.connect returns (0, "") if success, and (1, "error msg") if not
    def connect(self):
        if pymysql is None:
            WARNING("No pymysql module is found, exiting...")
        error = None
        for i in range(self.retry):
            try:
                self.conn = pymysql.connect(host = self.__host,
                                      port = self.__port,
                                      user = self.__user,
                                      passwd = self.__passwd,
                                      db = self.__dbname,
                                      connect_timeout = self.__connect_timeout,
                                      charset = self.__charset,
                                      use_unicode = self.__use_unicode
                                     )
            except Exception as e:
                error = e
                self.conn = None
                continue
            break
        if self.conn is None:
            return returnResult(1, error)
        return returnResult(0)

# query returns (rows, cursor) if success and (-1, e) if not.
    def query(self, sql, dictType = False, ex = False):
        if self.conn is None:
            return None
        # define cursor as a local variable
        if dictType:
            try:
                with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    try:
                        rows = cursor.execute(sql)
                    except Exception as e:
                        errcode, msg = e.args
                        return returnResult(errcode, msg)
                    result = cursor.fetchall()
                    if ex:
                        self.conn.commit()
                        self.lastrowid = cursor.lastrowid
                    return returnResult(rows, result)
            except Exception as e:
                    return returnResult(-1, e)
        else:
            try:
                with self.conn.cursor() as cursor:
                    rows = cursor.execute(sql)
                    result = cursor.fetchall()
                    if ex:
                        self.conn.commit()
                        self.lastrowid = cursor.lastrowid
                    return returnResult(rows, result)
            except Exception as e:
                    return returnResult(-1, e)

    def Query(self, sql, dictType = False):
        return decoupleResult(self.query(sql, dictType))

    def execute(self, sql):
        row, _ = decoupleResult(self.query(sql, False, True))
        if row < 0:
            return False
        return True

    def close(self):
        self.conn.close()
        self.conn = None

    def _reconnect(self):
        self.close()
        self.connect()

    def __del__(self):
        try:
            self.close()
        except Exception as e:
            pass


## connect to the database, if anything went wrong, it returns None, and the db handler if not.
class withConnectionTo(MysqlBase):
    def __enter__(self):
        conn = self.connect()
        if returnStatus(conn) != 0:
            ## connect error
            return None
        else:
            return self
    def __exit__(self, type, value, trace):
        self.__del__()

def ConnectionTo(host, port, user, passwd, dbname = "", charset="utf8mb4"):
    dbo = MysqlBase(host, port, user, passwd, dbname, charset)
    conn = dbo.connect()
    if returnStatus(conn) != 0:
        ## connect error
        return None
    else:
        return dbo
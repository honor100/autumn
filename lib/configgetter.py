#!/bin/env python3
# -*- coding: UTF-8 -*-

# File Name: configgetter.py
# Author: liuyunsong
# Mail: liuyunsong@xxx.cn
# Created Time: Sat 08 Apr 2017 04:46:22 PM CST

"""
get config
"""

import os, sys
import configparser
import subprocess
# from .util import WARNING
from .util import WARNING
from .X import Prpcrypt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + os.sep
pc = Prpcrypt()


class Configuration(object):
    def __init__(self, filename):
        self.__BASE_DIR = BASE_DIR
        self.__filename = self.__BASE_DIR + filename

        try:
            self.__reader = configparser.ConfigParser()
            self.__reader.read(self.__filename)
        except Exception as e:
            WARNING("get reader of ConfigParser failed.")
            self.__reader = None


    def get(self, section, option):
        if self.__reader == None:
            return None
        try:
            result = self.__reader.get(section, option)
        except Exception as e:
            WARNING("No [" + section +"]." + option + " in file " + self.__filename)
            return None
        return result

    def passget(self, section, option, salt_mask):
        if self.__reader == None:
            return None
        try:
            result = self.__reader.get(section, option)
            # cmd = """echo %s | base64 -d | cut -b 1,3,5,7,9,11-100""" % result
            # status, output = subprocess.getstatusoutput(cmd)
            # if status == 0:
            #     result = output
            # else:
            #     result = ""
            result = pc.b64decode(result, salt_mask).get('passwd')
        except Exception as e:
            WARNING("No [" + section +"]." + option + " in file " + self.__filename)
            return None
        return result


if __name__ == "__main__":
    conf = Configuration(".conf/mysql_mysqlha.conf")
    print(conf.get("client", "user"))
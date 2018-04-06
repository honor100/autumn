#!/bin/env python3
# -*- coding: UTF-8 -*-

# File Name: lib/logger.py
# Author: liuyunsong
# Mail: liuyunsong@xxx.cn
# Created Time: Mon 10 Apr 2017 05:12:44 PM CST

# root, prod, dev, debug
import os, sys
import logging
import logging.handlers
from . import configgetter


def getLogPath():
    getter = configgetter.Configuration("conf/global.conf")
    return getter.get("logs", "log_path")


def getLogRetainDays():
    getter = configgetter.Configuration("conf/global.conf")
    res = getter.get("logs", "retain_days")
    if res is None:
        return 7
    return res


logLevel = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

log_map = {}


def log(filename, message, loglevel="", logdir="", rotating=""):
    # level
    if loglevel:
        level = logLevel[loglevel.lower()]
    else:
        level = logging.INFO

    # logdir
    if not logdir:
        logdir = getLogPath()
        if not logdir:
            logdir = "/data/logs/"
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    # logfile
    logfile = os.path.join(logdir, filename)

    # retainDays
    retainDays = int(getLogRetainDays())

    # logger
    if filename in log_map:
        logger = log_map.get(filename)
    else:
        logger = logging.getLogger(filename);  # 获取名为filename的logger
        logger.setLevel(level)

        # handler, default rotating with TimedRotatingFileHandler
        if rotating == "size":
            handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=1 * 1024 * 1024 * 1024,
                                                           backupCount=retainDays);  # 实例化handler
        else:
            handler = logging.handlers.TimedRotatingFileHandler(logfile, when="D", interval=1,
                                                                backupCount=retainDays);  # 实例化handler

        # formatter
        fmt = "%(asctime)s [%(levelname)s] %(message)s"
        formatter = logging.Formatter(fmt);  # 实例化formatter
        handler.setFormatter(formatter);  # 为handler添加formatter

        # addHandler to logger
        logger.addHandler(handler);  # 为logger添加handler
        if loglevel.lower() == "debug":  # 为logger添加StreamHandler
            StreamHandler = logging.StreamHandler(sys.stdout, )
            StreamHandler.setFormatter(formatter)
            logger.addHandler(StreamHandler)
        # add logger to log_map for reuse
        log_map[filename] = logger

    logger.debug(message);
    logger.info(message);


## for the life of worker and fetcher
def LifeLog(message, loglevel=""):
    log("life.info", message, loglevel)


## for the items checked normally
def NormalLog(message, loglevel=""):
    log("normal.check", message, loglevel)


## for the items that is abnormal
def AbnormalLog(message, loglevel=""):
    log("abnormal.check", message, loglevel)


## for insert error
def InsertError(message, loglevel=""):
    log("sql.error", message, loglevel)


if __name__ == "__main__":
    log('normal.check', 'Hello body', logdir='/dev/shm/')
    # log('normal.check', 'Hello body', logdir='/dev/shm/',rotating="size")
    # log('normal.check','Hello body',loglevel='debug',logdir='/dev/shm/')
    # log('normal.check','Hello body',loglevel='debug',logdir='/dev/shm/',rotating="size")
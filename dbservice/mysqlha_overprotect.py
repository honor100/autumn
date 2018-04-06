#!/bin/env python3
# -*- coding: UTF-8 -*-

# File Name: mysqlha_overprotect.py
# Author: liuyunsong
# Mail: liuyunsong@xxx.cn
# Created Time: Mon 17 Apr 2017 10:48:47 AM CST

import os
import sys
import json
import random
import pymysql
import threading
from multiprocessing import Process
import time,datetime
from pathlib import Path

from multiprocessing import Pool # 进程池
from multiprocessing.dummy import Pool as ThreadPool # 线程池


BASE_DIR = Path(__file__).absolute().parent.parent
sys.path.insert(0,str(BASE_DIR))
from lib import mysqllib
from lib import maillib
from lib import daemonlib
from lib import configgetter
from lib import logger
from lib import util


# global variables
BASE_DIR = Path(__file__).parent.parent
SEND_MAIL_THRESHOLD = 10
LOGDIR = "/rzjf/logs/overprotect/"
QUERY_MAP = {1: {'Query'}, 2: {'Sleep'}, 12: {'Query','Sleep'}}

SYS_DB_WHITE_LIST = {"mysql","sys","performance_schema","information_schema","mondmm"}
SYS_USER_WHITE_LIST = {"autoddl","autogrants","autograntsss","automan","dbservice","ganglia","grafana","mon","myadmin","mysqlha","replica","root","superdba","xtra","xtrabackup"}


def timeBetween(t, start_time, end_time):
    if datetime.datetime.strptime(str(start_time),'%H:%M:%S') <= datetime.datetime.strptime(t,'%H:%M:%S') <= datetime.datetime.strptime(str(end_time),'%H:%M:%S'):
        return True
    else:
        return False

def sendMail(host, port, threshold, current, db, sql, item="慢查询"):
    now = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
    # product, role, idc = base.getProductFromHostPort(port, host)
    product, role, idc = ['重构项目','主库','演练环境']
    # subject = "[(%s)%s:%s(%s)](%s) [%s]" % (product, host, str(port), idc, role, item)
    subject = f"[({product}){host}:{port}({idc})]({role}) [{item}]"
    content = "product: %s\nhost: %s\nport: %s\nidc: %s\nrole: %s\nitem: %s\nthreshold: %s\ncurrent: %s\ninfo: [%s]%s\nsend at [%s]" % (
              product, host, str(port), idc, role, item, threshold, current, db, sql, now)
    mailto = ["liuyunsong@51rz.com"]
    _cc = ["zhangdongyang@51rz.com",
           "yangguangwei@51rz.com",
           "chenhailong@51rz.com",
           "luoziliang@51rz.com",
           "zhuerwei@51rz.com"
           ]
    if current >= 10:
        _cc.append("fanhuafeng@51rz.com")
        _cc.append("zhangsongjian@51rz.com")
    # maillib.sendMail(mailto, subject, content)
    random.randint(1,5)
    maillib.sendMail(mailto, subject, content, cc=_cc)


class Protect():
    CONFIG = configgetter.Configuration("conf/global.conf")
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr=LOGDIR+'error.log'):
        self.localhost_rw = Protect.CONFIG.get("overprotect_rw", "host")
        self.localport_rw = int(Protect.CONFIG.get("overprotect_rw", "port"))
        self.localuser_rw = Protect.CONFIG.get("overprotect_rw", "user")
        self.localpasswd_rw = Protect.CONFIG.passget("overprotect_rw", "passwd", Protect.CONFIG.get("overprotect_rw", "salt_mask"))
        self.localdb_rw = Protect.CONFIG.get("overprotect_rw", "db")

        self.localhost_r = Protect.CONFIG.get("overprotect_r", "host")
        self.localport_r = int(Protect.CONFIG.get("overprotect_r", "port"))
        self.localuser_r = Protect.CONFIG.get("overprotect_r", "user")
        self.localpasswd_r = Protect.CONFIG.passget("overprotect_r", "passwd", Protect.CONFIG.get("overprotect_r", "salt_mask"))
        self.localdb_r = Protect.CONFIG.get("overprotect_r", "db")
        # 程序执行间隔
        self.interval = int(Protect.CONFIG.get("overprotect_r", "interval"))

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    # get policy
    def getPolicy(self, dboR):
        now = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
        sql = "select host, port, db, query_type, query_time, batch, sleep, start_time, end_time, mail_alarm, kill_or_not " \
              "from overprotect_policy where status=1"
        row, results = dboR.Query(sql)
        if row < 0:
            # print("[%s]\tERROR: exec %s error" % (now, sql))
            logger.log("error.log", "ERROR: exec %s error" % (sql,), logdir=LOGDIR)
        elif row == 0:
            # print("[%s]\tOK,but the query get no data." % now)
            logger.log("error.log", "OK,but the query get no data.", logdir=LOGDIR)
        return row, results

        # get db white list

    def getDbWhiteList(self, dboR, host, port):
        rs = []
        now = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
        sql = "select db, start_time, end_time from overprotect_whitelist_db " \
              "where host='%s' and port=%d and status=1" % (host, port)
        row, results = dboR.Query(sql, True)
        if row > 0:
            for result in results:
                start_time = result['start_time']
                end_time = result['end_time']
                if timeBetween(now, start_time, end_time):
                    db = result['db']
                    rs.append(db)
        rs = set(rs)
        return rs

    # get user white list
    def getUserWhiteList(self, dboR, host, port):
        rs = []
        now = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
        sql = "select user, start_time, end_time from overprotect_whitelist_user " \
              "where host='%s' and port='%s' and status=1" % (host, port)
        row, results = dboR.Query(sql, True)
        if row > 0:
            for result in results:
                start_time = result['start_time']
                end_time = result['end_time']
                if timeBetween(now, start_time, end_time):
                    user = result['user']
                    rs.append(user)
        rs = set(rs)
        return rs

    # connect remote client under the protect and do something protect
    def ConnDoProtect(self, host, port, sql, query_time, batch, sleep, mail_alarm, kill_or_not):
        now = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
        user = Protect.CONFIG.get("mysqlha", "user")
        passwd = Protect.CONFIG.passget("mysqlha", "passwd", Protect.CONFIG.get("mysqlha", "salt_mask"))
        with mysqllib.withConnectionTo(host, port, user, passwd) as dboRClient:
            if dboRClient is None:
                # print("connect to %s:%s error" % (host, port))
                logger.log("error.log", "connect to %s:%s error" % (host, port), logdir=LOGDIR)
                return False
            else:
                row, results = dboRClient.Query(sql)
                if row < 0:
                    # print('''[%s]\tERROR: %s:%d exec %s error''' % (now, host, port, sql))
                    logger.log("error.log", '''ERROR: %s:%d exec %s error''' % (host, port, sql), logdir=LOGDIR)
                elif row == 0:
                    # print("[%s]\tGOOD, %s:%d have no long query!!!" % (now, host, port))
                    logger.log("normal.log", "GOOD, %s:%d have no long query!!!" % (host, port), logdir=LOGDIR)
                else:
                    with mysqllib.withConnectionTo(self.localhost_rw, self.localport_rw, self.localuser_rw,
                                                   self.localpasswd_rw, self.localdb_rw) as dboRW:
                        # print("%s:%d have have %d long query need killed" % (host, port, row))
                        logger.log("abnormal.log", "%s:%d have have %d long query need killed" % (host, port, row),
                                   logdir=LOGDIR)
                        suffix = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m')
                        today = datetime.date.today()
                        day = today.day
                        for index, result in enumerate(results):
                            query_id, user, client_host, db, command, client_time, state, info = result

                            # sql fingerprint
                            sql_template = util.formatSQL(info)
                            fingerprint = util.md5(sql_template)
                            sql = '''insert into overprotect_fingerprint(sql_template,fingerprint) ''' \
                                  '''values('%s','%s') ON DUPLICATE KEY UPDATE amount=amount+1''' % (
                                pymysql.escape_string(sql_template), fingerprint)
                            dboRW.execute(sql)
                            fingerprintId = dboRW.lastrowid

                            # send mail
                            if mail_alarm == 1 and client_time >= SEND_MAIL_THRESHOLD:
                                sendMail(host, port, query_time, client_time, db, info)

                            # log in db,create log table every month lastday
                            if day == 1:
                                dboRW.execute("create table if not exists overprotect_logs_%s like overprotect_logs" % suffix)

                            try:
                                sql = '''insert into overprotect_logs_%s(host,port,query_time,query_id,user,client_host,db,command,time,state,info,fingerprint_id) ''' \
                                      '''values('%s',%d,%d,%d,'%s','%s','%s','%s',%d,'%s','%s',%d)''' % (
                                    suffix, host, port, query_time, query_id, user, client_host,
                                    db, command, client_time, state, util.escape_string(info), fingerprintId
                                )
                                Flag = dboRW.execute(sql)
                                if Flag:
                                    logger.log("abnormal.log",
                                               "long query %d : [%s:%s][%s] %s" % (index + 1, user, client_host, db, info),
                                               logdir=LOGDIR)
                                else:
                                    logger.log("error.log", "Something is wrong,and sql=%s" % sql, logdir=LOGDIR)
                                # kill or not
                                # if kill_or_not == 1 and info[:6].lower() == "select":
                                if kill_or_not == 1:
                                    dboRClient.execute("kill %d" % query_id)
                                    logger.log("abnormal.log",
                                               "long query %d  runtime[%s] was killed" % (index + 1, client_time),
                                               logdir=LOGDIR)
                                    """
                                    if int(client_time) > 10:
                                        kill_sql_lists = get_kill_sql_lists()
                                        for kill_sql_list in kill_sql_lists:
                                            if kill_sql_list in info:
                                                dboRClient.execute("kill %d" % query_id)
                                                logger.log("abnormal.log","long query %d  runtime[%s] was killed" % (index+1,client_time), logdir=LOGDIR)
                                    """
                            except Exception as e:
                                logger.log("error.log", "Something is error:%s" % e, logdir=LOGDIR)
                            # kill every batch sleep some seconds,default is 20
                            if index % batch == 0:
                                time.sleep(sleep)
                return True

    def run(self):
        while True:
            # get start time
            start = datetime.datetime.now()
            # conntect to server to get policy and white lists
            with mysqllib.withConnectionTo(self.localhost_r, self.localport_r, self.localuser_r, self.localpasswd_r,
                                           self.localdb_r) as dboR:
                if dboR is None:
                    # print("connect to %s:%s error" % (self.localhost_r, self.localport_r))
                    logger.log("error.log", "connect to %s:%s error" % (self.localhost_r, self.localport_r),
                               logdir=LOGDIR)
                    sys.exit(1)
                # get policy
                row, results = self.getPolicy(dboR)
                if row <= 0:
                    time.sleep(self.interval)
                    continue

                # conntect to server to write logs
                # with mysqllib.withConnectionTo(self.localhost_rw, self.localport_rw, self.localuser_rw,
                #                                self.localpasswd_rw, self.localdb_rw) as dboRW:
                #     if dboR is None:
                #         # print("connect to %s:%s error" % (self.localhost_r, self.localport_r))
                #         logger.log("error.log", "connect to %s:%s error" % (self.localhost_r, self.localport_r),
                #                    logdir=LOGDIR)
                #         sys.exit(1)
                # traversal policy
                tpool = ThreadPool()  # 创建一个线程池
                # task_list= []
                for result in results:
                    host, port, db, query_type, query_time, batch, sleep, start_time, end_time, mail_alarm, kill_or_not = result
                    print (result)
                    print (db)
                    # db 为 ["%"] 的情况，先留下釦子，日后从页面添加时通过ajax获取
                    db = json.loads(db)
                    query_type = QUERY_MAP[query_type]
                    userWhiteList = self.getUserWhiteList(dboR, host, port) | SYS_USER_WHITE_LIST
                    dbWhiteList = self.getDbWhiteList(dboR, host, port) | SYS_DB_WHITE_LIST

                    # fix mysql can not math condition like (cell,)
                    query_type = query_type if len(query_type) > 1 else query_type | {""}
                    dbWhiteList = dbWhiteList if len(dbWhiteList) > 1 else dbWhiteList | {""}
                    userWhiteList = userWhiteList if len(userWhiteList) > 1 else userWhiteList | {""}

                    ## BEGIN TO KILL MYSQL LONG QUERY
                    if db == ["%"]:
                        # Filter policy0:
                        # if not dbWhiteList and not userWhiteList:
                        #     sql = """select id,user,host,db,command,time,state,info from information_schema.processlist """ \
                        #           """where command in {0} and time>={1} """ \
                        #           """order by time desc""".format(tuple(query_type), query_time)
                        # # Filter policy1:if db condition exists,the user condition will be ignore
                        # elif dbWhiteList:
                        #     dbWhiteList = dbWhiteList if len(dbWhiteList) > 1 else dbWhiteList | {""}
                        #     sql = """select id,user,host,db,command,time,state,info from information_schema.processlist """ \
                        #           """where command in {0} and time>={1} and db not in {2} """ \
                        #           """order by time desc""".format(tuple(query_type), query_time, tuple(dbWhiteList))
                        # elif userWhiteList:
                        #     userWhiteList = userWhiteList if len(userWhiteList) > 1 else userWhiteList | {""}
                        #     sql = """select id,user,host,db,command,time,state,info from information_schema.processlist """ \
                        #           """where command in {0} and time>={1} and user not in {2} """ \
                        #           """order by time desc""".format(tuple(query_type), query_time, tuple(userWhiteList))

                        sql = """select id,user,host,db,command,time,state,info from information_schema.processlist """ \
                              """where command in {0} and time>={1} and (db not in {2} or user not in {3}) """ \
                              """order by time desc""".format(tuple(query_type), query_time, tuple(dbWhiteList), tuple(userWhiteList))
                    else:
                        # if not dbWhiteList and not userWhiteList:
                        #     db = set(db) if len(db) > 1 else set(db) | {""}
                        #     sql = """select id,user,host,db,command,time,state,info from information_schema.processlist """ \
                        #           """where command in {0} and time>={1} and db in {2} """ \
                        #           """order by time desc""".format(tuple(query_type), query_time, tuple(db))
                        # # Filter policy1:if db condition exists,the user condition will be ignore
                        # elif dbWhiteList:
                        #     db = set(db) - set(dbWhiteList)
                        #     if db == set():
                        #         continue
                        #     else:
                        #         db = db if len(db) > 1 else db | {""}
                        #         sql = """select id,user,host,db,command,time,state,info from information_schema.processlist """ \
                        #               """where command in {0} and time>={1} and db in {2} """ \
                        #               """order by time desc""".format(tuple(query_type), query_time, tuple(db))
                        # elif userWhiteList:
                        #     db = set(db) if len(db) > 1 else set(db) | {""}
                        #     userWhiteList = userWhiteList if len(userWhiteList) > 1 else userWhiteList | {""}
                        #     sql = """select id,user,host,db,command,time,state,info from information_schema.processlist """ \
                        #           """where command in {0} and time>={1} and db in {2} and user not in {3} """ \
                        #           """order by time desc""".format(tuple(query_type), query_time, tuple(db),
                        #                                           tuple(userWhiteList))
                        db = set(db) - set(dbWhiteList)
                        if db == set():
                            continue

                    print (sql)


                    # self.ConnDoProtect(dboRW, host, port, sql, query_time, batch, sleep, mail_alarm, kill_or_not)
                    # timer = threading.Thread(target=self.ConnDoProtect, args=(host, port, sql, query_time, batch, sleep, mail_alarm, kill_or_not))
                    # timer.start()
                    # task_list.append(tpool.apply_async(self.ConnDoProtect, (host, port, sql, query_time, batch, sleep, mail_alarm, kill_or_not)))  # 将任务挨个发给线程池
                    tpool.apply_async(self.ConnDoProtect, (host, port, sql, query_time, batch, sleep, mail_alarm, kill_or_not))
                    # p = Process(target=self.ConnDoProtect, args=(host, port, sql, query_time, batch, sleep, mail_alarm, kill_or_not))
                    # p.start()
                tpool.close()
                tpool.join()
            #
            logger.log("normal.log", '=' * 45, logdir=LOGDIR)
            end = datetime.datetime.now()
            period = self.interval - (end - start).seconds
            if period <= 0:
                period = 1
            time.sleep(period)


if __name__ == '__main__':
    daemon = Protect("/var/run/overprotect.pid")
    # if len(sys.argv) >= 2:
    #     if 'start' == sys.argv[1]:
    #         daemon.start()
    #     elif 'stop' == sys.argv[1]:
    #         daemon.stop()
    #     elif 'restart' == sys.argv[1]:
    #         daemon.restart()
    #     else:
    #         print("Unknown command")
    #         sys.exit(2)
    #     sys.exit(0)
    # else:
    #     print("usage: %s start|stop|restart" % sys.argv[0])
    #     sys.exit(2)
    daemon.run()

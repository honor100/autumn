# -*- coding: utf-8 -*-

'''
2018-03-24
'''


import sys
import json
import pymysql
import time
import datetime

from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (
    DeleteRowsEvent,
    UpdateRowsEvent,
    WriteRowsEvent)

    
    
def loadPosition(filename="/home/tidb/binlog2dml/config/meta5000.json"):
    with open(filename,"r") as fd:
        d = json.load(fd)
        print("savePosition加载入文件完成...\n", d)
        return d
    
def savePosition(d):
    with open("/home/tidb/binlog2dml/config/meta5000.json","w") as fd:
        json.dump(d,fd)
        print("savePosition存入文件完成...\n", d)
        
SYNC_POSITION = loadPosition()
MYSQL_SETTINGS = {'host': '172.16.102.141', 'port': 5000, 'user': 'replicator', 'passwd': 'uoKos98RwA'}
DATA_MASKING = ["card_id","email","pre_mobile","reg_mobile","card_no","id_no","bank_no","mobile"]



def binLogStreamReader():
    stream = BinLogStreamReader(
        connection_settings=MYSQL_SETTINGS, 
        server_id=1024,
        log_file=SYNC_POSITION['master_log_file'],
        log_pos=SYNC_POSITION['master_log_pos'],
        #auto_position="97d304fb-f5d3-11e7-b1d5-00163f006549:1-3770281",    
        blocking=True,
        resume_stream=True, 
        # only_schemas,only_tables只能过滤DML语句
        only_schemas=["rz_account", "rz_user"],
        only_tables=["rz_account_bank", "rz_user", "rz_cg_user_ext"],
        only_events=[DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent]
        )
    return stream
    

        


    
def exceuteSQL(sql):
    try:
        conn=pymysql.connect(host='127.0.0.1',port=4000,user='root',passwd='rzjf@123!',charset='utf8mb4') #链接数据库 
        cur=conn.cursor()
        cur.execute(sql)
        #print(cur.fetchall())
        conn.commit()
    except Exception as e:
        print('Exception',e,sql)
    finally:
        if cur:
            cur.close() 
        if conn:
            conn.close() 


def main():    
    stream = binLogStreamReader()
    try:
        for binlogevent in stream:
            #binlogevent.dump() 
            time_local=time.localtime(binlogevent.timestamp)
            event_time=time.strftime("%Y-%m-%d %H:%M:%S",time_local)
            print("event_time:",event_time)
            print("event_type:",binlogevent.event_type)
            print("event_size:",binlogevent.event_size)
            Position = {
                #"schema": binlogevent.schema, 
                #"table": binlogevent.table, 
                "master_log_file": stream.log_file,
                "master_log_pos": stream.log_pos,
                #"auto_position": stream.auto_position,
                #"master_auto_position": binlogevent.packet.log_pos
                }
            #print(Position)
            #savePosition(Position)
            if binlogevent.event_type == 30:
                #insert
                for row in binlogevent.rows:
                    COLstr=''  #列字段 
                    ROWstr='' #行字段 
                    d = row['values']
                    for k,v in d.items():
                        if k in DATA_MASKING:
                            v = ''
                        if v is None or v == datetime.datetime.strptime('1970-01-01 08:00:00', "%Y-%m-%d %H:%M:%S"):
                            v = '0000-00-00 00:00:00'
                        if isinstance(v,str):
                            v = pymysql.escape_string(v)
                        COLstr = f"{COLstr}`{k}`,"  
                        ROWstr = f"{ROWstr}'{v}',"  
                    COLstr = COLstr.rstrip(',')    
                    ROWstr = ROWstr.rstrip(',')
                    sql = f"insert into {binlogevent.schema}.{binlogevent.table}({COLstr}) values({ROWstr})"
                    exceuteSQL(sql)                    
                    #sys.stdout.flush()
            if binlogevent.event_type == 31:
                #update
                for row in binlogevent.rows:
                    SETstr=''  #SET字段 
                    WHEREstr='' #WHERE字段 
                    after_values = row['after_values']
                    before_values = row['before_values']
                    for k,v in after_values.items():
                        if k in DATA_MASKING:
                            v = ''
                        if v is None or v == datetime.datetime.strptime('1970-01-01 08:00:00', "%Y-%m-%d %H:%M:%S"):
                            v = '0000-00-00 00:00:00'
                        if isinstance(v,str):
                            v = pymysql.escape_string(v)
                        SETstr = f"{SETstr}`{k}`='{v}',"
                    '''
                    for k,v in before_values.items():
                        if k in DATA_MASKING:
                            v = ''
                        if v is None or v == datetime.datetime.strptime('1970-01-01 08:00:00', "%Y-%m-%d %H:%M:%S"):
                            v = '0000-00-00 00:00:00'
                        WHEREstr = f"{WHEREstr}`{k}`='{v}' and "                     
                   '''
                    WHEREstr = "`ids`='%s'" % before_values.get('ids')                     
                    SETstr = SETstr.rstrip(',')    
                    #WHEREstr = WHEREstr.rstrip(' and ')
                    sql = f"update {binlogevent.schema}.{binlogevent.table} set {SETstr} where {WHEREstr}"
                    exceuteSQL(sql)             
                    #sys.stdout.flush()
            if binlogevent.event_type == 32:
                #delete
                for row in binlogevent.rows:
                    WHEREstr='' #WHERE字段 
                    d = row['values']
                    '''
                    for k,v in d.items():
                        if k in DATA_MASKING:
                            v = ''
                        if v == datetime.datetime.strptime('1970-01-01 08:00:00', "%Y-%m-%d %H:%M:%S"):
                            v = '0000-00-00 00:00:00'
                        WHEREstr = f"{WHEREstr}`{k}`='{v}',"   
                    '''
                    WHEREstr = "`ids`='%s'" % before_values.get('ids')                     
                    #WHEREstr = WHEREstr.rstrip(',')    
                    sql = f"delete from {binlogevent.schema}.{binlogevent.table} where {WHEREstr}"
                    exceuteSQL(sql)
                    #sys.stdout.flush()                    
            #print(Position)
            savePosition(Position)
    except KeyboardInterrupt:
        stream.close()
    except Exception as e:
        print(e)
    finally:
        stream.close()
        
        
        
if __name__ == "__main__":
    main()

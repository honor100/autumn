from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.event import QueryEvent

MYSQL_SETTINGS = {'host': '127.0.0.1', 'port': 3306, 'user': 'root', 'passwd': 'tongdun.cn'}

def binLogStreamReader():
    stream = BinLogStreamReader(
        connection_settings=MYSQL_SETTINGS, 
        server_id=1024,
        #log_file=SYNC_POSITION['master_log_file'],
        #log_pos=SYNC_POSITION['master_log_pos'],
        #auto_position="97d304fb-f5d3-11e7-b1d5-00163f006549:1-3770281",    
        #blocking=True,
        #resume_stream=True, 
        # only_schemas,only_tables只能过滤DML语句
        #only_schemas=["rz_account", "rz_user"],
        #only_tables=["rz_account_bank", "rz_user", "rz_cg_user_ext"],
        #only_events=[DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent]
        only_events=[QueryEvent]
        )
    return stream 

stream = binLogStreamReader()

for binlogevent in stream:
	#binlogevent.dump() 
	binlogevent.schema
	binlogevent.query

#!/bin/env python3
# -*- coding: UTF-8 -*-

# File Name: lib/maillib.py
# Author: liuyunsong
# Mail: liuyunsong@xxx.cn
# Created Time: Thu 13 Apr 2017 01:49:27 PM CST

import re, copy
import threading
from multiprocessing import Process

from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr
import smtplib

from . import configgetter, X
from .util import WARNING

def getMailConf():
    getter = configgetter.Configuration("conf/global.conf")
    show = getter.get("mail_sender", "show")
    sender = getter.get("mail_sender", "sender")
    keys = getter.get("mail_sender", "keys")
    code = getter.get("mail_sender", "code")
    smtp_server = getter.get("mail_sender", "smtp_server")
    smtp_port = int(getter.get("mail_sender", "smtp_port"))
    ssl = int(getter.get("mail_sender", "ssl"))
    return show, sender, keys, code, smtp_server, smtp_port, ssl


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def _sendMail(receiver, subject, content, type='', cc=""):
    receiver = list(receiver) if isinstance(receiver, (list,tuple)) else re.split(',|;', receiver)
    cc = list(cc) if isinstance(cc, (list,tuple)) else re.split(',|;', cc)
    toAll = copy.deepcopy(receiver)
    if cc != ['']:
        toAll.extend(cc)
    show, sender, keys, code, smtp_server, smtp_port, ssl = getMailConf()
    pc = X.Prpcrypt()
    code = pc.b64decode(code, keys)['passwd']
    # 邮件对象:
    msg = MIMEMultipart()
    msg['From'] = _format_addr(u'DB邮件 <%s>' % show)
    msg['To'] = ";".join(receiver)
    msg['cc'] = ';'.join(cc)
    msg['Subject'] = Header(subject, 'utf-8').encode()
    # 邮件正文是MIMEText:
    if type == 'html':
        msg.attach(MIMEText(content, 'html', 'utf-8'))
    else:
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
    # 添加附件就是加上一个MIMEBase
    """
    with open("./static/child.jpg", "rb") as fd:
        # 设置附件的MIME和文件名
        mime = MIMEBase('image', 'jpg', filename='child.jpg')
        # 加上必要的头信息:
        mime.add_header('Content-Disposition', 'attachment', filename='child.jpg')
        mime.add_header('Content-ID', '<0>')
        mime.add_header('X-Attachment-Id', '0')
        # 把附件的内容读进来:
        mime.set_payload(fd.read())
        # 用Base64编码:
        encoders.encode_base64(mime)
        # 添加到MIMEMultipart:
        msg.attach(mime)
    """

    try:
        if ssl == 1:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)  # 使用SSL
            # server = smtplib.SMTP_SSL('172.16.15.4', 465)  # 使用SSL
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)  # SMTP协议默认端口是25
        # server.set_debuglevel(1)
        server.login(sender, code)
        server.sendmail(sender, toAll, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        WARNING("邮件发送失败：%s" % e)
        return False


def sendMail(receiver, subject, content, type='', cc=""):
    # p = Process(target=_sendMail, args=(receiver, subject, content, type, cc))
    # p.start()
    timer = threading.Timer(0.1, _sendMail, (receiver, subject, content, type, cc))
    timer.start()

def formatHtmlContent(title, ths=[], tbs=[[]]):
    # imageUrl="cid:0"
    imageUrl = "https://ss0.bdstatic.com/94oJfD_bAAcT8t7mm9GUKT-xh_/timg?image&quality=100&size=b4000_4000&sec=1492143848&di=af9aa43a1e97e6fd2b6a1004628ee976&src=http://www.wallcoo.com/nature/HD_Vast_expanse_of_grassland/wallpapers/1280x1024/Wallcoo_com_Vast_summer_grassland_014.jpg"

    """Format the mail content to a html style"""
    thead = "".join(["<th>{0}</th>".format(th) for th in ths])

    def format_td(tb):
        return "".join(["<td>{0}</td>".format(item) for item in tb])

    tbody = "".join(["<tr>{0}</tr>".format(td) for td in [format_td(tb) for tb in tbs]])
    # FIXME: we can't use str.format() in here, it throws
    # KeyError when using str.format()
    content = """<html>
        <head>
        <title>%s</title>
        <meta http-equiv="content-type" content="text/html;charset=utf-8 ">
        </head>
        <style type="text/css">
        body{
          font-size: 12px;
          text-align: center;
          font-family: "Microsoft YaHei";
          background-image: url("%s");
          background-size: cover;
        }
        table{
          margin: 0 auto;
          border:1px solid #dddddd;
          border-radius: 4px;
          border-collapse: separate;
          border-left: 0;
          border-spacing: 0;
        }
        td{
           border-top: 1px solid #dddddd;
           text-align: left;
        }
        th,td{
          border-left: 1px solid #dddddd;
          padding: 8px ;
          line-height: 18px;
          text-align: left;
        }
        th{
          font-weight: bolder;
        }
        tbody tr:nth-child(2n+1) td{
         background: #f9f9f9;
        }
        </style>
        <body> 
          <h2 style="text-align: center;">%s</h2>
          <table width="900">
            <thead>
              <tr>%s</tr>
            </thead>
            <tbody>%s</tbody>
          </table>
        </body>
      </html>""" % (title, imageUrl, title, thead, tbody)

    return content


def sendHtmlMail(receiver, title, ths, tbs, cc=''):
    html = formatHtmlContent(title, ths, tbs)
    sendMail(receiver, title, html, 'html', cc)


if __name__ == "__main__":
    mailto = "liuyunsong@51rz.com"
    title = 'hello'
    msg = 'hello body'
    _cc = "fanhuafeng@51rz.com"
    # sendMail(mailto, title,msg)


    title = '数据库统计'
    thead = ['端口', '产品线', 'IP', '角色', '库名']
    results = (
        (5621, '旧版app', '172.16.1.156', '主库', 'wd'),
        (5621, '旧版app', '172.16.1.152', '从库', 'wd'),
        (5621, '旧版app', '172.16.1.151', '从库', 'wd'),
        (4010, '新版app', '172.16.1.156', '主库', 'new_wd'),
        (4010, '新版app', '172.16.1.152', '从库', 'new_wd'),
        (5000, '重构', '172.16.1.154', '主库', 'rzp2p'),
        (5000, '重构', '172.16.1.153', '从库', 'rzp2p'),
    )

    # map处理完成后再转一遍list,否则html处理会失败
    tbody = list(map(list, results))
    for tr in tbody:
        for index, td in enumerate(tr):
            if (index == 0 and td > 5000) or (index == 3 and td == '主库'):
                td = '<font color="red">{0}</font>'.format(td)
                tr[index] = td
    sendHtmlMail(mailto, title, thead, tbody)
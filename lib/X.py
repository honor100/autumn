#!/bin/env python3
# -*- coding: UTF-8 -*-

# File Name: lib/X.py
# Author: liuyunsong
# Mail: liuyunsong@xxx.cn
# Created Time: Tue 11 Apr 2017 05:51:16 PM CST

import sys
import random
import base64
import hashlib
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex



class Prpcrypt():
    def __init__(self, key="https://tsinghua.edu.cn.", iv=b'010-110402430053'):
        #这里密钥key 长度必须为16（AES-128）,24（AES-192）,或者32 （AES-256）Bytes 长度。
        self.key = key
        self.iv  = iv
        self.mode = AES.MODE_CBC
        self.BS = AES.block_size

        #补位至AES.block_size的倍数
        self.pad = lambda s: s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)
        self.unpad = lambda s : s[0:-ord(s[-1])]


    def getSaltMap(self, passwd, salt_length=0, salt_mask=0):
        # generate salts：salt_mask有值以salt_mask为准，否则以salt_length来生成
        if passwd and salt_mask and len(str(salt_mask)) <= len(passwd):
            salt_mask_list = [int(i) for i in str(salt_mask)]
        elif passwd and 0 < salt_length <= len(passwd):
            # 确保salt_list[0]不为0，且每一项都不大于salt_length
            salt_mask_list = [random.randint(1, salt_length)]
            salt_mask_list = salt_mask_list + [random.randint(0, salt_length) for i in range(salt_length - 1)]
            salt_mask = int(''.join([str(i) for i in salt_mask_list]))
        else:
            # salt_length and salt_mask must have one,and when use salt_length,it must be less than passwd salt_length
            raise Exception("Please enter the correct parameters")
        # encrypt salt_mask
        salt_mask = ''.join([chr(int(i)+109) for i in str(salt_mask)])
        # generate salts
        chars = """AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz1234567890~`!@#$%^&*()-_+={}[]\|:;'",.<>/?"""
        salts = "".join([random.choice(chars) for mask in salt_mask_list])
        # 加盐
        passwd_list = list(passwd)
        for index, mask in enumerate(salt_mask_list):
            passwd_list.insert(mask, salts[index])
        passwd = "".join(passwd_list)

        saltMap = {'salt_mask': salt_mask, 'salt_mask_list': salt_mask_list, 'salts': salts, 'passwd': passwd}
        return saltMap


    def encrypt(self, passwd, salt_length=0, salt_mask=0):
        if passwd:
            if salt_length or salt_mask:
                saltMap = self.getSaltMap(passwd, salt_length, salt_mask)
            else:
                saltMap = {'salt_mask': 0, 'salt_mask_list': [], 'salts': '', 'passwd': passwd}
        else:
            raise Exception("Please enter the correct parameters")
        # 补位，补足16的倍数
        passwd = self.pad(saltMap['passwd'])
        # 加密：目前AES-128 足够目前使用
        cryptor = AES.new(self.key, self.mode, self.iv)
        cipher_passwd = cryptor.encrypt(passwd)
        #因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        #所以这里统一把加密后的字符串转化为16进制字符串
        # 先把cipher_passwd转换成二进制数据然后在用十六进制表示，也可使用hexlify()和unhexlify()
        cipher_passwd = b2a_hex(cipher_passwd)
        ciphertext = {'cipher_passwd': cipher_passwd, 'salt_mask': saltMap['salt_mask'], 'salts': saltMap['salts']}
        return ciphertext


    def decrypt(self, cipher_passwd, salt_mask=0):
        if not cipher_passwd:
            raise Exception("Please enter the correct parameters")
        # 与b2a_hex相反
        cipher_passwd = a2b_hex(cipher_passwd)
        # 解密
        cryptor = AES.new(self.key, self.mode, self.iv)
        plain_passwd = cryptor.decrypt(cipher_passwd)
        # 除去填充
        plain_passwd = self.unpad(plain_passwd.decode('utf-8'))
        plain_passwd_list = list(plain_passwd)
        # 去盐
        try:
            salt_mask_list = [(ord(i) - 109) for i in salt_mask]
        except TypeError:
            salt_mask_list = [int(i) for i in str(salt_mask)]
        # 排除没有填充位的情况
        if salt_mask_list != [0]:
            while salt_mask_list:
                mask = int(salt_mask_list.pop())
                plain_passwd_list.pop(mask)
        passwd = "".join(plain_passwd_list)
        plaintext = {"passwd": passwd, 'salt_mask': salt_mask}
        return plaintext


    # 加密后生成md5值，适用存储在数据库做密码比对
    def md5(self, passwd, salt_length=0, salt_mask=0):
        ciphertext = self.encrypt(passwd, salt_length, salt_mask)
        cipher_passwd = ciphertext['cipher_passwd']
        md5 = hashlib.md5(cipher_passwd).hexdigest()
        ciphertext['md5'] = md5
        return ciphertext


    # 加密后生成sha1值，适用存储在数据库做密码比对
    def sha1(self, passwd, salt_length=0, salt_mask=0):
        ciphertext = self.encrypt(passwd, salt_length, salt_mask)
        cipher_passwd = ciphertext['cipher_passwd']
        sha1 = hashlib.sha1(cipher_passwd).hexdigest()
        ciphertext['sha1'] = sha1
        return ciphertext


    def b64encode(self, passwd, salt_length=0, salt_mask=0):
        if passwd:
            if salt_length or salt_mask:
                saltMap = self.getSaltMap(passwd, salt_length, salt_mask)
            else:
                saltMap = {'salt_mask': 0, 'salt_mask_list': [], 'salts': '', 'passwd': passwd}
        else:
            raise Exception("Please enter the correct parameters")
        # 补位，补足3的倍数
        passwd = saltMap['passwd'] + (3 - len(saltMap['passwd']) % 3) * chr(3 - len(saltMap['passwd']) % 3)
        # 加密：base64.b64encode()
        cipher_passwd = base64.b64encode(passwd.encode('utf-8')).decode('utf-8')
        ciphertext = {'cipher_passwd': cipher_passwd, 'salt_mask': saltMap['salt_mask'], 'salts': saltMap['salts']}
        return ciphertext

    def b64decode(self, cipher_passwd, salt_mask=0):
        if not cipher_passwd:
            raise Exception("Please enter the correct parameters")
        # 解密：base64.b64decode()
        plain_passwd = base64.b64decode(cipher_passwd).decode('utf-8')
        # 除去填充
        plain_passwd = plain_passwd[0:-ord(plain_passwd[-1])]
        plain_passwd_list = list(plain_passwd)
        # 去盐
        try:
            salt_mask_list = [(ord(i) - 109) for i in salt_mask]
        except TypeError:
            salt_mask_list = [int(i) for i in str(salt_mask)]
        # 排除没有填充位的情况
        if salt_mask_list != [0]:
            while salt_mask_list:
                mask = int(salt_mask_list.pop())
                plain_passwd_list.pop(mask)
        passwd = "".join(plain_passwd_list)
        plaintext = {"passwd": passwd, 'salt_mask': salt_mask}
        return plaintext







if __name__ == "__main__":
    pc = Prpcrypt()
    e = pc.encrypt("1234567890", salt_length=6)
    print(e)
    e = pc.encrypt("1234567890", salt_mask=147369)
    print(e)
    d = pc.decrypt(e["cipher_passwd"], salt_mask=e["salt_mask"])
    print(d)
    e = pc.md5("1234567890", salt_mask=147369)
    print(e)
    e = pc.sha1("1234567890", salt_length=6)
    print(e)
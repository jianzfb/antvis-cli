# -*- coding: UTF-8 -*-
# @Time    : 2021/10/8 2:41 下午
# @File    : tt2.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

from qiniu import Auth, put_file, etag, put_stream, put_data
import qiniu.config
from qiniu import BucketManager
import os
import requests
# 需要填写你的 Access Key 和 Secret Key
access_key = 'ZSC-X2p4HG5uvEtfmn5fsTZ5nqB3h54oKjHt0tU6'
secret_key = 'Ya8qYwIDXZn6jSJDMz_ottWWOZqlbV8bDTNfCGO0'

#构建鉴权对象
q = Auth(access_key, secret_key)
#要上传的空间
bucket_name = 'image'
#上传后保存的文件名
key = 'UI/my-python-logo_vv.png'
#生成上传 Token，可以指定过期时间等
token = q.upload_token(bucket_name, None, 3600)

#要上传文件的本地路径
localfile = '/Users/jian/Downloads/iqiyi_1610978950796 (1).png'
# ret, info = put_file(token, key, localfile, version='v2')
# with open(localfile, 'rb') as fp:
#   ret, info = put_stream(token, key, fp, file_name, len(input_stream))

# with open(localfile, 'rb') as fp:
#   content = fp.read()
#   ret, info = put_data(token, key, content)
#   print(info)

# print(info)
# print(info)
# assert ret['key'] == key
# assert ret['hash'] == etag(localfile)


bucket = BucketManager(q)
bucket_name = 'image'
# 前缀
prefix = 'ss'
# 列举条目
limit = None
# 列举出除'/'的所有文件以及以'/'为分隔的所有前缀
delimiter = None
# 标记
marker = None
ret, eof, info = bucket.list(bucket_name, prefix, marker, limit, delimiter)
use_size = sum([s['fsize']/1024/1024 for s in ret['items']])
print(info)

#
# #有两种方式构造base_url的形式
# key = 'ss/my-python-logo_vv.png'
# base_url = 'http://image.mltalker.com/%s' % ( key)
# # #或者直接输入url的方式下载
# # base_url = 'http://domain/key'
# #可以设置token过期时间
# private_url = q.private_download_url(base_url, expires=3600)
# print(private_url)
# r = requests.get(private_url)

with open("python_logo.png", 'wb') as f:
  f.write(r.content)
assert r.status_code == 200
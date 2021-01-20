# -*- coding: UTF-8 -*-
# @Time    : 2020/7/23 7:33 下午
# @File    : __init__.py.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from antvis.client import mlogger
import os
import tarfile
import json
import uuid
from antvis.client.mlogger.metric.base import *
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging


class FileLogger(object):
    def __init__(self, title):
        self.group_name = ''
        self.tag = ''
        self.title = title
        assert title != ''

        # experiment config
        self.project = mlogger.getEnv().dashboard.project
        self.experiment_name = mlogger.getEnv().dashboard.experiment_name
        self.experiment_uuid = mlogger.getEnv().dashboard.experiment_uuid
        self.folder = ''

        if self.experiment_uuid is None:
            return

    @property
    def name(self):
        return self.title

    @name.setter
    def name(self, val):
        group_name = ''
        self.tag = val
        if '/' in val:
            group_name, self.tag = val.split('/')
        self.group_name = group_name

    def update(self, *args, **kwargs):
        # 支持WEBDAV, MLTALKER
        # antvis/experiment_uuid/group/%s_(latest_%d).xxx
        if len(args) == 0:
            return

        local_file_path = os.path.normpath(args[0])
        if not os.path.exists(local_file_path):
            return
        # 扩展名
        ext_name = local_file_path.split('.')[-1]
        # 文件名
        file_name = local_file_path.split('/')[-1]

        # 单位M
        fsize = os.path.getsize(local_file_path)
        fsize = fsize / float(1024 * 1024)
        fsize = round(fsize, 2)

        # 1.step 获得临时秘钥
        response = \
          mlogger.getEnv().dashboard.rpc.cos.experiment.get(file_size=fsize,
                                                            operator='upload')
        if response['status'] == 'ERROR':
          logging.error('could get cos credential')
          return

        tmpSecretId = response['content']['tmpSecretId']
        tmpSecretKey = response['content']['tmpSecretKey']
        sessionToken = response['content']['sessionToken']
        region = response['content']['region']
        bucket = response['content']['bucket']

        # 2.step 上传文件
        tag_str = self.tag if self.group_name == '' else '%s/%s' % (self.group_name, self.tag)
        try:
          config = CosConfig(Region=region,
                             SecretId=tmpSecretId,
                             SecretKey=tmpSecretKey,
                             Token=sessionToken,
                             Scheme='https')
          client = CosS3Client(config)
          with open(local_file_path, 'rb') as fp:
            client.put_object(
                Bucket=bucket,
                Body=fp,
                Key='{}/{}/{}/{}'.format(self.experiment_uuid, tag_str, self.title, file_name),
                StorageClass='STANDARD',
                EnableMD5=False
              )
        except:
          logging.error('upload {} error'.format(local_file_path))
          return

        # 3.step 更新平台记录
        mlogger.getEnv().dashboard.experiment.patch(**{
            'experiment_name': self.experiment_name,
            'experiment_uuid': self.experiment_uuid,
            'experiment_stage': mlogger.getEnv().dashboard.experiment_stage,
            'experiment_data': json.dumps({'FILE_ABSTRACT': {
                'group': tag_str,
                'title': self.title,
                'backend': 'ANTVIS',
                'path': '{}/{}/{}/{}'.format(self.experiment_uuid, tag_str, self.title, file_name),
                'size': fsize,
            }, 'APP_STAGE': mlogger.getEnv().dashboard.experiment_stage})
        })

    def config(self, **kwargs):
        pass

    def get(self):
        # 文件下载
        # 1.step 获取日志文件
        tag_str = self.tag if self.group_name == '' else '%s/%s' % (self.group_name, self.tag)
        response = \
            mlogger.getEnv().dashboard.\
                rpc.experiment.file.get(experiment_uuid=self.experiment_uuid,
                                        key='{}/{}'.format(tag_str, self.title))
        if response['status'] == 'ERROR':
          logging.error('couldnt get log file path')
          return

        log_file = response['content']['path']
        log_name = log_file.split('/')[-1]
        tmpSecretId = response['content']['tmpSecretId']
        tmpSecretKey = response['content']['tmpSecretKey']
        sessionToken = response['content']['sessionToken']
        region = response['content']['region']
        bucket = response['content']['bucket']

        # 2.step 下载日志文件
        try:
          config = CosConfig(Region=region,
                             SecretId=tmpSecretId,
                             SecretKey=tmpSecretKey,
                             Token=sessionToken,
                             Scheme='https')
          client = CosS3Client(config)
          response = client.get_object(Bucket=bucket, Key=log_file)
          file_content = response['Body'].get_raw_stream()
          with open('./{}'.format(log_name), 'wb') as fp:
            fp.write(file_content.read())
        except:
          logging.error('download {} error'.format(log_file))


class FolderLogger(FileLogger):
    def __init__(self, title):
        super(FolderLogger, self).__init__(title)
        self.group_name = ''
        self.file_title = title
        assert title != ''

    def update(self, *args, **kwargs):
        # antvis/experiment_uuid/group/%s_(latest_%d).xxx
        if len(args) == 0:
            return

        local_folder_path = args[0]
        if not os.path.exists(local_folder_path):
            return

        if not os.path.isdir(local_folder_path):
            return

        # 压缩打包
        tar_file_name = '%s.tar.gz' % (self.file_title)
        tar = tarfile.open('./'+tar_file_name, 'w:gz')
        for root, dirs, files in os.walk(local_folder_path):
            rel_root = os.path.relpath(root, local_folder_path)
            for f in files:
                tar.add(os.path.join(root, f), arcname=os.path.join(rel_root, f))
        tar.close()

        # 上传
        super(FolderLogger, self).update('./'+tar_file_name)

        # 清空临时压缩包
        os.remove('./'+tar_file_name)

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
import sys
from antvis.client.mlogger.metric.base import *
import logging
# 七牛云接口
from qiniu import Auth, put_file, etag
import qiniu.config
# 阿里云盘接口
from aligo import Aligo
import requests
import zlib


# aliyun:   使用个人存储空间
# qiniu:    使用平台空间
# dist:     本地
class FileLogger(object):
    root_folder = '/antvis'
    cache_folder = './logger/cache'
    def __init__(self, title, backend='aliyun', only_record=False):
        self.title = title
        assert title != ''

        self.is_ready = False
        # backend storage
        self.backend = backend
        if self.backend is not None and self.backend not in ['aliyun', 'qiniu', 'disk', 'hdfs']:
            logging.error('FileLogger only support (aliyun,qiniu,disk,hdfs) backend')
            return

        self.ali = None
        self.only_record = only_record
        if self.backend is not None and self.backend == 'aliyun':
            self.ali = Aligo()

        # experiment config
        self.project = mlogger.getEnv().dashboard.project
        self.experiment_name = mlogger.getEnv().dashboard.experiment_name
        self.experiment_uuid = mlogger.getEnv().dashboard.experiment_uuid

        self.is_ready = True

    def ali_mkdir(self, remote_path, p=False):
        # remote prefix
        remote_path = remote_path.replace('ali://', '')
        remote_path = os.path.normpath(remote_path)
        # 迭代创建目录
        levels = remote_path.split('/')[1:]
        level_num = len(levels)
        find_file = None
        find_i = level_num
        for i in range(level_num,-1,-1):
            check_path = '/'+'/'.join(levels[:i])            
            find_file = self.ali.get_folder_by_path(check_path)
            if find_file:
                break
            find_i = i - 1

        if find_i == level_num:
            # 已经存在，不进行重新创建
            return find_file.file_id

        sub_folder = '/'.join(levels[find_i:])
        ss = self.ali.create_folder(sub_folder,find_file.file_id)
        return ss.file_id

    @property
    def name(self):
        return self.title

    @name.setter
    def name(self, val):
        pass

    def update(self, *args, **kwargs):
        if len(args) == 0:
            return
        if not self.is_ready:
            return
        if self.experiment_name is None or self.experiment_name == '':
            return
        if self.experiment_uuid is None or self.experiment_uuid == '':
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

        if self.backend == 'aliyun':
            # 上传到阿里云盘并在平台记录
            remote_folder = 'ali://'
            if FileLogger.root_folder != '':
                remote_folder = FileLogger.root_folder
            remote_folder = remote_folder.replace('ali://', '')
            if remote_folder.endswith('/'):
                remote_folder = remote_folder[:-1]

            if self.ali is None:
                self.ali = Aligo()

            file_id = self.ali_mkdir(remote_folder, True)
            if not self.only_record:
                # 上传
                self.ali.upload_file(local_file_path, file_id)

            # 记录
            mlogger.getEnv().dashboard.experiment.patch(**{
                'experiment_name': self.experiment_name,
                'experiment_uuid': self.experiment_uuid,
                'experiment_stage': mlogger.getEnv().dashboard.experiment_stage,
                'experiment_data': zlib.compress(json.dumps(
                    {
                        'FILE_ABSTRACT': {
                            'title': self.title,
                            'backend': self.backend,
                            'path': f'{remote_folder}/{file_name}',
                            'size': fsize,
                            'group': f'{file_id}'
                        },
                        'APP_STAGE': mlogger.getEnv().dashboard.experiment_stage
                    }
                ).encode())
            })
            return

        if self.backend == 'disk':
            if not self.only_record:
                # do nothing
                pass

            disk_address = kwargs.get('address', 'unkown')
            # 记录
            mlogger.getEnv().dashboard.experiment.patch(**{
                'experiment_name': self.experiment_name,
                'experiment_uuid': self.experiment_uuid,
                'experiment_stage': mlogger.getEnv().dashboard.experiment_stage,
                'experiment_data': zlib.compress(json.dumps(
                    {
                        'FILE_ABSTRACT': {
                            'title': self.title,
                            'backend': f'disk',
                            'path': f'{disk_address}?{local_file_path}',
                            'size': fsize,
                        }, 
                        'APP_STAGE': mlogger.getEnv().dashboard.experiment_stage
                    }
                ).encode())
            })
            return

        # 腾讯COS
        # # 1.step 获得临时秘钥
        # response = \
        #   mlogger.getEnv().dashboard.rpc.cos.experiment.get(file_size=fsize,
        #                                                     operator='upload')
        # if response['status'] == 'ERROR':
        #   logging.error('could get cos credential')
        #   return
        #
        # tmpSecretId = response['content']['tmpSecretId']
        # tmpSecretKey = response['content']['tmpSecretKey']
        # sessionToken = response['content']['sessionToken']
        # region = response['content']['region']
        # bucket = response['content']['bucket']
        #
        # # 2.step 上传文件
        # tag_str = self.tag if self.group_name == '' else '%s/%s' % (self.group_name, self.tag)
        # try:
        #   config = CosConfig(Region=region,
        #                      SecretId=tmpSecretId,
        #                      SecretKey=tmpSecretKey,
        #                      Token=sessionToken,
        #                      Scheme='https')
        #   client = CosS3Client(config)
        #   with open(local_file_path, 'rb') as fp:
        #     client.put_object(
        #         Bucket=bucket,
        #         Body=fp,
        #         Key='{}/{}/{}/{}'.format(self.experiment_uuid, tag_str, self.title, file_name),
        #         StorageClass='STANDARD',
        #         EnableMD5=False
        #       )
        # except:
        #   logging.error('upload {} error'.format(local_file_path))
        #   return

        # 七牛COS
        # 1.step 获得临时秘钥
        info = mlogger.getEnv().getUploadToken('log/file')
        if info is None:
            logging.error('Could get cos token (maybe exceed your storage limit).')
            return None
        token = info['token']
        user = info['user']
        
        remote_path = 'antvis/{}/{}/{}'.format(self.experiment_uuid, self.title, file_name)
        ret, info = put_file(token, remote_path, local_file_path, version='v2')
        if info.status_code != 200:
            logging.error('Fail to upload.')
            return

        # 3.step 更新平台记录
        mlogger.getEnv().dashboard.experiment.patch(**{
            'experiment_name': self.experiment_name,
            'experiment_uuid': self.experiment_uuid,
            'experiment_stage': mlogger.getEnv().dashboard.experiment_stage,
            'experiment_data': zlib.compress(json.dumps(
                {
                    'FILE_ABSTRACT': {
                        'title': self.title,
                        'backend': 'qiniu',
                        'path': remote_path,
                        'size': fsize,
                    }, 
                    'APP_STAGE': mlogger.getEnv().dashboard.experiment_stage
                }
            ).encode())
        })

    def config(self, **kwargs):
        pass

    def get(self, filter_key=None):
        # 文件下载
        if not self.is_ready:
            return None

        os.makedirs(FileLogger.cache_folder, exist_ok=True)

        response = mlogger.getEnv().dashboard.rpc.experiment.file.get(
            experiment_uuid=self.experiment_uuid,
            title=self.title,
        )
        if response['status'] == 'ERROR':
            logging.error('Couldnt get record info.')
            return None

        record_info = response['content']
        remote_info_list = record_info['files']
        project_name = record_info.get('project_name', None)
        if project_name is not None:
            project_name = project_name.split('.')[-1]

        local_file_list = []
        remote_file_list = []
        for file_info in remote_info_list:
            file_backend = file_info['backend']
            file_path = file_info['path']
            file_url = file_info['url']
            file_name = file_path.split('/')[-1]

            if filter_key is not None:
                if file_name != filter_key:
                    continue

            if os.path.exists(os.path.join(FileLogger.cache_folder, file_name)):
                local_file_list.append(os.path.join(FileLogger.cache_folder, file_name))
                if file_backend == 'aliyun':
                    remote_file_list.append(file_path.replace('ali://', ''))
                elif file_backend == 'qiniu':
                    remote_file_list.append(file_url)
                else:
                    remote_file_list.append(file_path)
                continue

            if file_backend == 'aliyun':
                if self.ali is None:
                    self.ali = Aligo()

                file_path = file_path.replace('ali://', '')
                file = self.ali.get_file_by_path(file_path)
                if file is None:
                    logging.error(f'Remote file path {file_path} not exist')
                    return None

                self.ali.download_file(file=file, local_folder=FileLogger.cache_folder)
                local_file_list.append(os.path.join(FileLogger.cache_folder, file_name))
                remote_file_list.append(file_path)

            if file_backend == 'disk':
                remote_address, remote_path = '', file_path
                if "?" in file_path:
                    remote_address, remote_path = file_path.split('?')

                create_time = remote_path.split('/')[2]
                if '@' not in remote_address:
                    # only for test
                    remote_address = input("please remote address (user@ip):\n")
                os.system(f'scp {remote_address}:~/{create_time}/{project_name}/{remote_path} {FileLogger.cache_folder}')
                file_name = remote_path.split('/')[-1]
                local_path = f'{FileLogger.cache_folder}/{file_name}'
                local_file_list.append(file_path)
                remote_file_list.append(remote_path)

            if file_backend == 'qiniu':
                try:
                    r = requests.get(file_url, stream=True)
                    with open(os.path.join(FileLogger.cache_folder, file_name), "wb") as pdf:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                pdf.write(chunk)
                    local_file_list.append(os.path.join(FileLogger.cache_folder, file_name))
                    remote_file_list.append(file_url)
                except:
                    logging.error('Download {} error.'.format(file_name))                

        return local_file_list, remote_file_list


class FolderLogger(FileLogger):
    def __init__(self, title, backend='aliyun', only_record=False):
        super(FolderLogger, self).__init__(title, backend, only_record)

    def update(self, *args, **kwargs):
        if len(args) == 0:
            return
        if not self.is_ready:
            return

        local_folder_path = args[0]
        if not os.path.exists(local_folder_path):
            return

        if not os.path.isdir(local_folder_path):
            return

        # 压缩打包
        tar_file_name = '%s.tar.gz' % (self.title)
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


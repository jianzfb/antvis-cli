# -*- coding: UTF-8 -*-
# @Time    : 2020/7/23 7:33 下午
# @File    : __init__.py.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from antvis.client import mlogger
import os
from webdav3.client import *
from webdav3.exceptions import LocalResourceNotFound
import tarfile
import json
import uuid


class FileLogger(object):
    def __init__(self, title):
        self.group_name = ''
        self.tag = ''
        self.file_title = title
        # experiment config
        self.project = mlogger.getEnv().dashboard.project
        self.experiment_name = mlogger.getEnv().dashboard.experiment_name
        self.experiment_uuid = mlogger.getEnv().dashboard.experiment_uuid
        self.folder = ''
        
        if self.experiment_uuid is None:
            return
        
        # webdav config
        self.webdav_host = mlogger.getEnv().webdav_host
        self.webdav_login = mlogger.getEnv().webdav_login
        self.webdav_password = mlogger.getEnv().webdav_password
        self.webdav_root = mlogger.getEnv().webdav_root

        self.webdav_client = None
        if mlogger.getEnv().use_webdav:
            if self.webdav_host is not None and self.webdav_login is not None and self.webdav_password is not None:
                try:
                    # 创建客户端
                    options = {
                        'webdav_hostname': self.webdav_host,
                        'webdav_login': self.webdav_login,
                        'webdav_password': self.webdav_password,
                        'disable_check': True,  # 有的网盘不支持check功能
                    }
                    self.webdav_client = Client(options)
                except:
                    print('webdav fail connect')
                    self.webdav_client = None
        self.init_flag = False
        
    @property
    def name(self):
        return self.file_title

    @name.setter
    def name(self, val):
        group_name = ''
        self.tag = val
        if '/' in val:
            group_name, self.tag = val.split('/')

        self.group_name = group_name
        if self.group_name != '':
            self.folder = '%s/antvis/%s/%s'%(self.webdav_root, self.experiment_uuid, self.group_name)
        else:
            self.folder = '%s/antvis/%s'%(self.webdav_root, self.experiment_uuid)

    def update(self, *args, **kwargs):
        # 支持WEBDAV, MLTALKER
        # antvis/experiment_uuid/group/%s_(latest_%d).xxx
        if len(args) == 0:
            return
        
        local_file_path = args[0]
        if not os.path.exists(local_file_path):
            return
        # 扩展名
        ext_name = local_file_path.split('.')[-1]

        if self.webdav_client is not None:
            try:
                if not self.init_flag:
                    # 首次调用,准备目录结构
                    if self.webdav_client is not None:
                        self.webdav_client.mkdir('%s/antvis' % (self.webdav_root))
                        self.webdav_client.mkdir('%s/antvis/%s' % (self.webdav_root, self.experiment_uuid))
                        if self.group_name != '':
                            self.webdav_client.mkdir(
                                '%s/antvis/%s/%s' % (self.webdav_root, self.experiment_uuid, self.group_name))
                    self.init_flag = True
                
                # 远程路径
                remote_file_path = \
                    os.path.join(self.folder,
                                 '%s.%s'%(self.file_title, ext_name))

                # 尝试删除已存在文件
                try:
                    self.webdav_client.clean(remote_file_path)
                except RemoteResourceNotFound as e:
                    pass
                except Exception as e:
                    pass

                # 更新文件
                self.webdav_client.upload(remote_file_path, local_file_path)
                print('finish upload file %s'%local_file_path)

                # 记录文件摘要
                mlogger.getEnv().dashboard.experiment.patch(**{
                    'experiment_name': self.experiment_name,
                    'experiment_uuid': self.experiment_uuid,
                    'experiment_stage': mlogger.getEnv().dashboard.experiment_stage,
                    'experiment_data': json.dumps({'FILE_ABSTRACT': {
                        'group': self.group_name,
                        'title': self.file_title,
                        'backend': 'WEBDAV',
                        'path': remote_file_path,
                        
                    }, 'APP_STAGE': mlogger.getEnv().dashboard.experiment_stage})
                })
            except Exception as e:
                print(e)
        else:
            tag_str = self.tag if self.group_name == '' else '%s/%s'%(self.group_name, self.tag)
            mlogger.getEnv().dashboard.rpc.file.upload(file=local_file_path,
                                                       slicing=True,
                                                       tag=tag_str,
                                                       experiment_stage=mlogger.getEnv().dashboard.experiment_stage)
            
    def config(self, **kwargs):
        pass

    def get(self):
        # 文件下载
        tag_str = self.tag if self.group_name == '' else '%s/%s' % (self.group_name, self.tag)
        mlogger.getEnv().dashboard.rpc.file.download(self.file_title, tag=tag_str)


class FolderLogger(FileLogger):
    def __init__(self, title):
        super(FolderLogger, self).__init__(title)
        self.group_name = ''
        self.file_title = title
        if self.file_title == '':
            self.file_title = str(uuid.uuid4())

    def update(self, *args, **kwargs):
        # 支持WEBDAV, MLTALKER
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
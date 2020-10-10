# -*- coding: UTF-8 -*-
# @Time    : 2020-06-01 10:32
# @File    : dashboard.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from antvis.client.job import *
from antvis.utils.utils import *
from antvis.client.httprpc import *
import json
import requests
import logging


class Dashboard(object):
    def __init__(self,
                 dashboard_ip=None,
                 dashboard_port=None,
                 token=None,
                 experiment_uuid=None):
        self._dashboard_ip = dashboard_ip
        self._dashboard_port = dashboard_port
        self._dashboard_prefix = 'antvis'
        self.launch_time = timestamp()
        self.quiet = False
        self._project = None
        self._experiment_name = None
        
        self._server = "FREE"
        self._experiment_uuid = None
        self._token = None
        self._hyper_parameter = ''
        self._stage = ''       # TRAIN, CHALLENGE, EXPERIMENT, ALL
        
        # 信息提交模块
        self.job = Job(self)
        self.job.start()

        # http rpc
        self.rpc = HttpRpc("v1",
                           self.dashboard_prefix,
                           self.dashboard_ip,
                           self.dashboard_port)
        if token is not None:
            self.token = token                          # 任务token
        if experiment_uuid is not None:
            self.experiment_uuid = experiment_uuid      # 实验uuid
        
    @property
    def project(self):
        return self._project
    
    @project.setter
    def project(self, val):
        self._project = val
    
    @property
    def experiment_name(self):
        return self._experiment_name
    
    @experiment_name.setter
    def experiment_name(self, val):
        self._experiment_name = val
    
    @property
    def server(self):
        return self._server
    
    @server.setter
    def server(self, val):
        self._server = val
        if self.rpc is not None:
            self.rpc.data.update({'experiment_context': self.server})

    @property
    def experiment_uuid(self):
        return self._experiment_uuid
    
    @experiment_uuid.setter
    def experiment_uuid(self, val):
        self._experiment_uuid = val
        if self.rpc is not None:
            self.rpc.data.update({'experiment_uuid': self.experiment_uuid})
    
    @property
    def token(self):
        return self._token
    
    @token.setter
    def token(self, val):
        self._token = val
        if self.rpc is not None:
            self.rpc.token = val
    
    @property
    def experiment_hyper_parameter(self):
        return self._hyper_parameter
    
    @experiment_hyper_parameter.setter
    def experiment_hyper_parameter(self, val):
        self._hyper_parameter = val
    
    @property
    def dashboard_ip(self):
        return self._dashboard_ip
    
    @dashboard_ip.setter
    def dashboard_ip(self, val):
        self._dashboard_ip = val
        if self.rpc is not None:
            self.rpc.ip = val
    
    @property
    def dashboard_port(self):
        return self._dashboard_port

    @dashboard_port.setter
    def dashboard_port(self, val):
        self._dashboard_port = val
        if self.rpc is not None:
            self.rpc.port = int(val)
    
    @property
    def dashboard_prefix(self):
        return self._dashboard_prefix
    
    @dashboard_prefix.setter
    def dashboard_prefix(self, val):
        self._dashboard_prefix = val
        if self.rpc is not None:
            self.rpc.prefix = val
    
    @property
    def experiment_stage(self):
        return self._stage
    
    @experiment_stage.setter
    def experiment_stage(self, val):
        self._stage = val

    def create_channel(self, channel_name, channel_type, **kwargs):
        return self.job.create_channel(channel_name, channel_type, **kwargs)

    def create_chart(self, chart_channels, chart_title, chart_x_axis="x", chart_y_axis="y", **kwargs):
        return self.job.create_chart(chart_channels, chart_title, chart_x_axis, chart_y_axis, **kwargs)
    
    def create_project(self, *args, **kwargs):
        # 1.step 配置dashboard
        self.configure(*args, **kwargs)
        
        # 2.step 创建项目(获得 experiment_uuid)
        response = \
            self.rpc.experiment.post(task_name=self.project,
                                     experiment_name=self.experiment_name)
        experiment_uuid = None
        if response['status'] == "OK":
            experiment_uuid = response['content']['experiment_uuid']
            self.experiment_uuid = experiment_uuid
            
            self.rpc.data.update({'experiment_uuid': experiment_uuid})
            logging.info('success to create %s/%s'%(self.project, self.experiment_name))
        else:
            self.experiment_uuid = None
            logging.error('fail to register experiment in dashboard')


        return experiment_uuid

    def activate(self, project, experiment):
        if project is None or experiment is None:
            print('must set project and experiment')
            return

        # 1.step 获得experiment_uuid
        response = self.rpc.experiment.activate.get(experiment_name=experiment, project_name=project)
        if response['status'] == 'OK':
            self.experiment_uuid = response['content']['experiment_uuid']
            self.experiment_name = experiment
            self.project = project
            print('activate experiment %s/%s'%(response['content']['project_name'], response['content']['experiment_name']))
            # 更新rpc的实验标识字段
            self.rpc.data.update({'experiment_uuid': self.experiment_uuid})
        else:
            print('couldnt activate %s/%s'%(project, experiment))

    def list(self, project=None):
        response = self.rpc.experiment.list.get(project_name=project)
        if response['status'] == 'OK':
            return response['content']['experiment_list']

        return []

    def configure(self, *args, **kwargs):
        self.dashboard_ip = kwargs.get('dashboard_ip', self.dashboard_ip)
        self.dashboard_port = kwargs.get('dashboard_port', self.dashboard_port)
        
        token = kwargs.get('token', self.token)
        if token is not None:
            self.token = token

        experiment_uuid = kwargs.get('experiment_uuid', self.experiment_uuid)
        if experiment_uuid is not None:
            self.experiment_uuid = experiment_uuid

        server = kwargs.get('server', self.server)
        if server is not None:
            self.server = server
          
        self.project = kwargs.get('project', self.project)
        self.experiment_name = kwargs.get('experiment', self.experiment_name)
        
    def update(self):
        # update dashboard
        self.job.update()
    
    def exit(self):
        # exit dashboard
        # exit resource
        self.job.exit()

        # stop flag
        self.rpc.experiment.stop.post()

    def error(self):
        # exit resource
        self.job.exit()

        # error flag
        self.rpc.experiment.error.post()

    def __getattr__(self, key):
        if key in ['experiment', 'task', 'apply', 'dataset', 'challenge', 'benchmark']:
            return getattr(self.rpc, key)
        
        return self.__dict__.get(key)
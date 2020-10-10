# -*- coding: UTF-8 -*-
# @Time    : 2020-06-23 12:58
# @File    : __init__.py.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from antvis.client.dashboard import *
from antvis.client.mlogger.container import *
from antvis.client.mlogger.metric import *
from antvis.client.mlogger.complex import *
from antvis.client.mlogger.monitor import *
from antvis.client.mlogger.file import *
from contextlib import contextmanager
import git


class __Env(object):
    def __init__(self, ip, port, project=None, experiment=None, token=None):
        self.dashboard = Dashboard(ip, port, token=token)
        if project is not None and experiment is not None:
            self.dashboard.create_project(project=project, experiment=experiment)
        
        self._webdav_host = None
        self._webdav_login = None
        self._webdav_password = None
        self._webdav_root = ''
        self.use_webdav = False
        
    def create_chart(self, *args, **kwargs):
        return self.dashboard.create_chart(*args, **kwargs)
        
    def create_channel(self, *args, **kwargs):
        return self.dashboard.create_channel(*args, **kwargs)
    
    @property
    def webdav_host(self):
        return self._webdav_host
    
    @property
    def webdav_login(self):
        return self._webdav_login
    
    @property
    def webdav_password(self):
        return self._webdav_password
    
    @property
    def webdav_root(self):
        return self._webdav_root
    
    def webdav(self, host, login, password, root=''):
        self._webdav_host = host
        self._webdav_login = login
        self._webdav_password = password
        self._webdav_root = root
        self.use_webdav = True
    
        
__env = None


def getEnv():
    global __env
    return __env


def config(ip, port, project=None, experiment=None, token=None):
    global __env
    __env = __Env(ip, port, project, experiment, token)
    
    
def update():
    global __env
    __env.dashboard.update()
    
    
def exit():
    global __env
    __env.dashboard.exit()


def error():
    global __env
    __env.dashboard.error()


def create_project(project, experiment):
    # 创建实验
    global __env
    experiment_uuid = __env.dashboard.create_project(project=project, experiment=experiment)
    return experiment_uuid


def activate(project, experiment):
    # 激活指定实验
    global __env
    experiment_uuid = __env.dashboard.activate(project=project, experiment=experiment)
    return experiment_uuid


def list(project=None):
    # 获得实验列表
    global __env
    experiment_list = __env.dashboard.list(project=project)
    return experiment_list


@contextmanager
def Context(ip, port, project, experiment, token=None, path='.'):
    # 创建实验基本信息
    global __env
    global tag
    # 配置平台
    assert(project is not None and experiment is not None)
    config(ip, port, project, experiment, token)

    # 获取git信息
    git_commit = ''
    git_branch = ''
    try:
        repo = git.Repo(path)
        git_branch = repo.active_branch.name
        commits = list(repo.iter_commits(git_branch, max_count=1))
        if len(commits) > 0:
            git_commit = commits[0]
    except:
        print('project %s experiment %s no git info'%(project, experiment))

    # 配置实验信息
    tag.source.name = ''                # source identify (git URL, source file name, notebook name)
    tag.source.type = 'UNKOWN'          # source type. NOTEBOOK,PROJECT,UNKOWN
    tag.source.git.commit = git_commit  # commit hash of excuted code
    tag.source.git.branch = git_branch  # name of branch of excuted code
    tag.source.git.repourl = ''         # URL that executed code was cloned from
    tag.project.env = ''                # runtime context docker / conda
    tag.project.entrypoint = ''         # name of project entry point associated with experiment run
    tag.docker.image.name = ''          # name of docker image used to execute experiment run
    tag.docker.image.id = ''            # id of docker image used to execute experiment run
    tag.user = ''                       # identify of user who created experiment run
    tag.note.content = ''               # a descriptive note about experiment run
    tag.runname = ''                    # human readable name that identify experiment run

    try:
        yield
    except:
        # 实验错误
        error()
        return

    # 更新&退出
    update()
    exit()


class Tag(object):
    def __init__(self, parent='', parent_tag=None):
        self._tags = {}
        self._parent = parent
        self._parent_tag = parent_tag
        self._value = None

    def __setattr__(self, key, value):
        if key.startswith('_'):
            return super(Tag, self).__setattr__(key, value)

        self.__dict__['_tags'][key] = Tag('%s/%s'%(self._parent, key), self)
        value_str = str(value)
        self._value = value_str
        self.__update('%s/%s'%(self._parent, key), value_str)

    def __getattr__(self, item):
        if item == 'get':
            def _func():
                if self._parent_tag.__dict__['_value'] is not None:
                    return self._parent_tag.__dict__['_value']

                data = mlogger.getEnv().dashboard.rpc.experiment.tag.get(tag=self._parent)
                if data['status'] == 'OK':
                    return data['content']

                return ''
            return _func

        if item not in self._tags:
            self.__dict__['_tags'][item] = Tag('%s/%s'%(self._parent, item), self)

        return self._tags[item]

    def __update(self, key, value):
        getEnv().dashboard.job.cache({'TAG': {key: value}})


tag = Tag()
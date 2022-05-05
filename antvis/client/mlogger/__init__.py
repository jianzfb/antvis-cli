# -*- coding: UTF-8 -*-
# @Time    : 2020-06-23 12:58
# @File    : __init__.py.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from antvis.client.dashboard import *
from antvis.client.mlogger.container import *
from antvis.client.mlogger.variable import *
from antvis.client.mlogger.metric import *
from antvis.client.mlogger.complex import *
from antvis.client.mlogger.monitor import *
from antvis.client.mlogger.file import *
from contextlib import contextmanager
import git
import logging
from qiniu import put_data
from io import BytesIO


class __Env(object):
    def __init__(self, project=None, experiment=None, token=None, **kwargs):
        self.dashboard = Dashboard(token=token, **kwargs)
        if project is not None and experiment is not None:
            self.dashboard.create_project(project=project, experiment=experiment)

        self.cache_upload_token = {}

    def create_chart(self, *args, **kwargs):
        return self.dashboard.create_chart(*args, **kwargs)
        
    def create_channel(self, *args, **kwargs):
        return self.dashboard.create_channel(*args, **kwargs)

    def getUploadToken(self, mode):
        if mode not in self.cache_upload_token or (time.time() - self.cache_upload_token[mode]['time']) > self.cache_upload_token[mode]['expire']:
            response = \
                self.dashboard.rpc.cos.experiment.get(cos='QINIU', mode=mode, operator='upload')
            if response['status'] == 'ERROR':
                logging.error('Could get cos token (maybe exceed your storage limit).')
                return None

            self.cache_upload_token[mode] = response['content']
            self.cache_upload_token[mode].update({
                'time': time.time()
            })

        return self.cache_upload_token[mode]


__env = None


def getEnv():
    global __env
    return __env


def config(project=None, experiment=None, token=None, **kwargs):
    global __env
    __env = __Env(project, experiment, token, **kwargs)
    Variable.env = __env


def update():
    global __env
    if __env is None:
        return
    if __env.dashboard is not None:
        __env.dashboard.update()
    
    
def exit():
    global __env
    if __env is None:
        return
    if __env.dashboard is not None:
        __env.dashboard.exit()


def error():
    global __env
    if __env is None:
        return
    if __env.dashboard is not None:
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
def Context(project, experiment, token=None, path='.'):
    # 创建实验基本信息
    global __env
    global tag
    # 配置平台
    assert(project is not None and experiment is not None)
    config(project, experiment, token)

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
        logging.error('Project %s experiment %s no git info'%(project, experiment))

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

    yield

    # 更新&退出
    update()


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
                    return data['content']['value']

                return ''
            return _func

        if item not in self._tags:
            self.__dict__['_tags'][item] = Tag('%s/%s'%(self._parent, item), self)

        return self._tags[item]

    def __update(self, key, value):
        getEnv().dashboard.job.cache({'TAG': {key: value}})


tag = Tag()

# 更新任意信息
class Info(object):
    def __init__(self):
        pass

    def __getattr__(self, key):
        if getEnv().dashboard is not None:
            return getattr(getEnv().dashboard, key)


info = Info()

# 更新任意文件
class File(object):
    def __init__(self):
        pass

    def upload(self, prefix, name, content, is_file=False):
        result = getEnv().getUploadToken(prefix)
        token = result['token']
        user = result['user']

        key = 'antvis/{}/{}/{}'.format(user, prefix, name)
        if not is_file:
            ret, info = put_data(token, key, content)
        else:
            file_path = content
            if not os.path.exists(file_path):
                logging.error('Fail to upload %s (%s not exist).' % (name, file_path))
                return
            ret, info = put_file(token, key, file_path)

        if info.status_code != 200:
            logging.error('Fail to upload %s.'%name)
            return False

        return True

    def download(self, prefix, name, user, url=None):
        key = '.'.join([k for k in [prefix, name, user] if k is not None])
        if url is None:
            url = 'http://experiment.mltalker.com'
            key = 'antvis/{}/{}/{}'.format(user, prefix, name)

        f = BytesIO()
        try:
            r = requests.get(f'{url}/{key}', stream=True)
            if r.status_code != 200:
                logging.error('Fetch {} error.'.format(key))
                return None
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        except:
            logging.error('Fetch {} error.'.format(key))
            return None

        return f.getvalue()


file = File()

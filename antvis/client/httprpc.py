# -*- coding: UTF-8 -*-
# @Time    : 2020-06-01 11:54
# @File    : httprpc.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
import requests
import json
import os
import tarfile
import sys
import urllib
import uuid


class Resource(object):
    def __init__(self, rpc, resource):
        self._rpc = rpc
        self._resource = resource

    def slicing_upload(self, tag, **kwargs):
        # only support single file
        values = kwargs.values()
        if len(values) == 0:
            return

        file_path = list(kwargs.values())[0]
        if not os.path.exists(file_path):
            return

        if self._rpc.data is not None and type(self._rpc.data) == dict:
            kwargs.update(self._rpc.data)

        file_name = os.path.normpath(file_path).split('/')[-1]
        file_id = str(uuid.uuid4())
        file_size = os.path.getsize(file_path)
        chunk_size = 1024*1024 # 1M
        chunk_num = (file_size + chunk_size - 1)//chunk_size
        finished_size = 0
        api_url = '%s/upload/%s/' % (self._rpc.url, self._resource)
        try_times = 3
        fail_blocks = {}
        with open(file_path, 'rb') as fp:
            for chunk_id in range(chunk_num):
                remained_size = chunk_size
                if finished_size + chunk_size < file_size:
                    remained_size = chunk_size
                else:
                    remained_size = finished_size+chunk_size - file_size
                content = fp.read(remained_size)
                kwargs.update({'chunk_id': chunk_id, 'chunk_num': chunk_num, 'file_id':file_id, 'file_name': file_name, 'file_tag': tag})

                result = requests.post(api_url, kwargs, files={'file': content}, headers=self._rpc.headers)
                if result.status_code not in [200, 201]:
                    fail_blocks[chunk_id] = content
                    if len(fail_blocks) > 100:
                        print('always fail update, exit')
                        return

        if len(fail_blocks) > 0:
            for chunk_id, chuck_content in fail_blocks.items():
                result = requests.post(api_url, kwargs, files={'file': content}, headers=self._rpc.headers)
                if result.status_code not in [200, 201]:
                    print('always fail update, exit')
                    return

    def upload(self, *args, **kwargs):
        is_slicing = False
        if 'slicing' in kwargs:
            is_slicing = kwargs['slicing']
            kwargs.pop('slicing')
        tag = ''
        if 'tag' in kwargs:
            tag = kwargs['tag']
            kwargs.pop('tag')

        if is_slicing:
            # 开启分片上传
            response = self.slicing_upload(tag, **kwargs)
            return response

        files = {}
        for k, v in kwargs.items():
            if os.path.isdir(v):
                # compress
                normal_path = os.path.normpath(v)
                compressed_file_name = normal_path.split('/')[-1]
                compressed_file_path = os.path.join('/'.join(normal_path.split('/')[0:-1]), '%s.tar.gz' % compressed_file_name)

                if os.path.exists(compressed_file_path):
                    os.remove(compressed_file_path)

                tar = tarfile.open(compressed_file_path, 'w:gz')
                for f in os.listdir(v):
                    if f[0] == ".":
                        continue
                    tar.add(os.path.join(v, f), arcname=os.path.join(compressed_file_name, f))
                tar.close()
                
                v = compressed_file_path
            
            if not os.path.exists(v):
                continue
            
            if not k.startswith('FILE'):
                k = 'FILE_'+k
            files[k] = open(v, 'rb')
            
        if len(files) == 0:
            return {'status': 'ERROR', 'message': 'no files'}

        if self._rpc.data is not None and type(self._rpc.data) == dict:
            kwargs.update(self._rpc.data)
        
        api_url = '%s/upload/%s/' % (self._rpc.url, self._resource)

        result = requests.post(api_url, kwargs, files=files, headers=self._rpc.headers)
        if result.status_code not in [200, 201]:
            return {'status': 'ERROR'}

        response = json.loads(result.content)
        return response

    def __mkdir_p(self, dirname):
        """ make a dir recursively, but do nothing if the dir exists"""
        assert dirname is not None
        if dirname == '' or os.path.isdir(dirname):
            return
        try:
            os.makedirs(dirname)
        except OSError as e:
            if e.errno != 17:
                raise e

    # def __download(self, url, dir, fname=None):
    #     self.__mkdir_p(dir)
    #     if fname is None:
    #         fname = url.split('/')[-1]
    #     fpath = os.path.join(dir, fname)
    #
    #     def _progress(count, block_size, total_size):
    #         sys.stdout.write('\r>> downloading %s %.1f%%' %
    #                          (fname,
    #                           min(float(count * block_size) / total_size,
    #                               1.0) * 100.0))
    #         sys.stdout.flush()
    #
    #     try:
    #         fpath, _ = urllib.request.urlretrieve(url, fpath, reporthook=_progress)
    #         statinfo = os.stat(fpath)
    #         size = statinfo.st_size
    #     except:
    #         print("failed to download {}".format(url))
    #         return None
    #
    #     sys.stdout.write('\n')
    #     print('succesfully downloaded ' + fname + " " + str(size) + ' bytes.')
    #     return fpath

    def __get_file_name(self, headers):
        filename = ''
        if 'Content-Disposition' in headers and headers['Content-Disposition']:
            disposition_split = headers['Content-Disposition'].split(';')
            if len(disposition_split) > 1:
                if disposition_split[1].strip().lower().startswith('filename='):
                    filename = disposition_split[1].split('=')[-1]

        return filename

    def download(self, *args, **kwargs):
        # download and uncompress
        to_folder = kwargs.get('file_folder', "./")
        self.__mkdir_p(to_folder)

        download_file_name = ''
        if 'file_name' in kwargs:
            download_file_name = kwargs['file_name']

        if 'file_folder' in kwargs:
            kwargs.pop('file_folder')

        if self._rpc.data is not None and type(self._rpc.data) == dict:
            for k, v in self._rpc.data.items():
                if k not in kwargs:
                    kwargs.update({k: v})
        
        file_api_url = '%s/download/%s/' % (self._rpc.url, self._resource)
        is_success = True
        try:
            r = requests.get(file_api_url, kwargs, stream=True, headers=self._rpc.headers)
            file_name = self.__get_file_name(r.headers)
            if file_name != '' and download_file_name == '':
                download_file_name = file_name

            if download_file_name == '':
                download_file_name = str(uuid.uuid4())

            with open(os.path.join(to_folder, download_file_name), "wb") as pf:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        pf.write(chunk)

            print('successfully download {}'.format(download_file_name))
        except:
            print('failed to download {}'.format(download_file_name))
            if os.path.exists(os.path.join(to_folder, download_file_name)) and \
                    os.path.isfile(os.path.join(to_folder, download_file_name)):
                os.remove(os.path.join(to_folder, download_file_name))

            is_success = False

        if download_file_name.endswith('.tar.gz'):
            # uncompress
            tar = tarfile.open(os.path.join(to_folder, download_file_name))
            tar.extractall(to_folder)
            tar.close()
            print('successfully untar {}'.format(download_file_name))
    
        return {'status': 'SUCCESS'} if is_success else {'status': 'ERROR'}
    
    def __getattr__(self, action):
        if action not in ['get', 'post', 'put', 'patch', 'delete', 'upload', 'download']:
            return Resource(self._rpc, '%s/%s' % (self._resource, action))

        def func(*argc, **kwargs):
            api_url = '%s/%s/'%(self._rpc.url, self._resource)
            if self._rpc.data is not None and type(self._rpc.data) == dict:
                kwargs.update(self._rpc.data)
            
            try:
                if action == 'get':
                    result = requests.get(api_url, kwargs, headers=self._rpc.headers)
                    if result.status_code not in [200, 201]:
                        return {'status': 'ERROR'}
                    response = json.loads(result.content)
                    return response
                elif action == 'post':
                    result = requests.post(api_url, kwargs, headers=self._rpc.headers)
                    if result.status_code not in [200, 201]:
                        return {'status': 'ERROR'}
                    response = json.loads(result.content)
                    return response
                elif action == 'put':
                    result = requests.put(api_url, kwargs, headers=self._rpc.headers)
                    if result.status_code not in [200, 201]:
                        return {'status': 'ERROR'}
                    response = json.loads(result.content)
                    return response
                elif action == 'patch':
                    result = requests.patch(api_url, kwargs, headers=self._rpc.headers)
                    if result.status_code not in [200, 201]:
                        return {'status': 'ERROR'}
                    response = json.loads(result.content)
                    return response
                elif action == 'delete':
                    result = requests.delete(api_url, data=kwargs, headers=self._rpc.headers)
                    if result.status_code not in [200, 201]:
                        return {'status': 'ERROR'}
                    response = json.loads(result.content)
                    return response
                elif action == 'upload':
                    return None
                else:
                    return None
            except:
                return {'status': 'ERROR', 'message': 'connection error'}
            
        return func

        
class HttpRpc(object):
    def __init__(self, version, prefix, ip, port, token=None, **kwargs):
        self._ip = ip
        self._port = port
        self._prefix = prefix
        self._version = version
        self._token = token
        self._data = kwargs
    
    @property
    def version(self):
        return self._version
    
    @version.setter
    def version(self, val):
        self._version = val
    
    @property
    def ip(self):
        return self._ip
    
    @ip.setter
    def ip(self, val):
        self._ip = val
    
    @property
    def port(self):
        return self._port
    
    @port.setter
    def port(self,val):
        self._port = val
    
    @property
    def prefix(self):
        return self._prefix
    
    @prefix.setter
    def prefix(self, val):
        self._prefix = val
    
    @property
    def version(self):
        return self._version
    
    @version.setter
    def version(self, val):
        self._version = val
    
    @property
    def token(self):
        return self._token
    
    @token.setter
    def token(self, val):
        self._token = val
        
    @property    
    def url(self):
        request_url = 'http://%s:%d/%s' % (self.ip, self.port, self.prefix)
        return request_url
        
    @property
    def headers(self):
        if self.token is None:
            return None
        
        authorization = {'Authorization': "token " + self.token}
        return authorization
    
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, val):
        self._data = val
    
    def __getattr__(self, resource):
        return Resource(self, resource)

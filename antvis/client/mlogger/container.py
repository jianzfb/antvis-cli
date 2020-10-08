# -*- coding: UTF-8 -*-
# @Time    : 2020-06-25 23:28
# @File    : container.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function


class Container(object):
    def __init__(self):
        self._name = ''
        self._type = ''
        self._logger_obj = {}
    
    @property
    def name(self):
        return self._name

    @property
    def metrics(self):
        return [v for k,v in self._logger_obj.items() if v.logger_type == 'metric']

    def __setattr__(self, key, value):
        if key.startswith('_'):
            return super(Container, self).__setattr__(key, value)
        
        if type(value) == Container:
            if self.name != '':
                object.__setattr__(value, '_name', '{}/{}'.format(self.name, key))
            else:
                object.__setattr__(value, '_name', key)
        else:
            if self.name != '':
                value.name = '{}/{}'.format(self.name, key)
            else:
                value.name = key
                
        self.__dict__['_logger_obj'][key] = value
    
    def __getattr__(self, item):
        # if item not in self._logger_obj:
        #     return object.__getattribute__(self, item)
        if item not in self._logger_obj:
            return self.__dict__[item]

        return self.__dict__['_logger_obj'][item]

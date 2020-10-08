# -*- coding: UTF-8 -*-
# @Time    : 2020-06-29 22:30
# @File    : base.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

import numpy as np
import time

from collections import defaultdict, OrderedDict
from antvis.client import mlogger


class Base(object):
    charts = {}
    
    def __init__(self, plot_title, logger_type='metric', **kwargs):
        """ Basic metric
        """
        self.plot_title = plot_title
        self.chart_x_axis = ''
        self.chart_y_axis = ''
        self.channel = None
        self.chart = None
        self.reset_hooks_on_update()
        self.reset_hooks_on_log()
        self.time = 0
        self.logger_type = logger_type
        self.channel_config = kwargs

    def config(self, **kwargs):
        if 'x_axis' in kwargs:
            self.chart.x_axis = kwargs['x_axis']
            kwargs.pop('x_axis')

        if 'y_axis' in kwargs:
            self.chart.y_axis = kwargs['y_axis']
            kwargs.pop('y_axis')

        self.channel.params.update(kwargs)

    def update(self, *args, **kwargs):
        self._update(*args, **kwargs)
        for hook in self.hooks_on_update:
            hook()
        self.time += 1
        return self
    
    @property
    def name(self):
        return self.channel.channel_name
    
    @name.setter
    def name(self, val):
        self.channel.channel_name = val
        
        group_name = ''
        if '/' in val:
            group_name, _ = val.split('/')
            
        if self.chart is None:
            group_plot_title = self.plot_title
            if group_name != '':
                group_plot_title = '{}/{}'.format(group_name, self.plot_title)

            if group_plot_title not in Base.charts:
                Base.charts[group_plot_title] = mlogger.getEnv().create_chart([], group_plot_title)
            self.chart = Base.charts[group_plot_title]
            self.chart.chart_x_axis = self.chart_x_axis
            self.chart.chart_y_axis = self.chart_y_axis
        
        self.chart.bind_channel(self.channel)
        
    def reset_hooks_on_update(self):
        self.hooks_on_update = ()

    def reset_hooks_on_log(self):
        self.hooks_on_log = ()

    def hook_on_update(self, hook):
        self.hooks_on_update += (hook,)

    def hook_on_log(self, hook):
        self.hooks_on_log += (hook,)

    def _update(self, *args, **kwargs):
        raise NotImplementedError("_update should be re-implemented for each metric")

    def log(self):
        v = getattr(self, 'value', None)
        if v is not None:
            print('%s - value %f'%(self.chart.chart_title, v))

    def get(self):
        channel_name = self.channel.channel_name
        chart_name = self.chart.chart_title

        rpc = mlogger.getEnv().dashboard.rpc
        data = \
            rpc.experiment.chart.get(chart_name=chart_name,
                                     channel_name=channel_name)
        if data['status'] == 'OK':
            return data['content']
        return {}
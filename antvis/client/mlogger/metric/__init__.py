# -*- coding: UTF-8 -*-
# @Time    : 2020-06-25 23:28
# @File    : __init__.py.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
import numpy as np
import time
import uuid

from collections import defaultdict, OrderedDict
from antvis.client.mlogger.metric.base import *
from antvis.client.dashboard import *
from antvis.client import mlogger


class Simple(Base):
    def __init__(self, plot_title, **kwargs):
        super(Simple, self).__init__(plot_title, **kwargs)
        self.chart_x_axis = 'time'
        self.chart_y_axis = ''
        
        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)

    @property
    def value(self):
        return self._val
    
    def _update(self, val):
        self._val = float(val)
        self.channel.update(self.time, self.value)
        
        
class Accumulator_(Base):
    """
    Credits to the authors of pytorch/tnt for this.
    """
    def __init__(self,plot_title=None, **kwargs):
        super(Accumulator_, self).__init__(plot_title, **kwargs)
        self.chart_x_axis = 'time'
        self.chart_y_axis = ''

        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)
        self.reset()
        
    def reset(self):
        self._avg = 0
        self._total_weight = 0
        return self

    def _update(self, val, weighting=1):
        val, weighting = float(val), float(weighting)
        assert weighting > 0
        r = self._total_weight / (weighting + self._total_weight)
        self._avg = r * self._avg + (1 - r) * val
        self._total_weight += weighting
        
        # update
        self.channel.update(self.time, self.value)
        
    @property
    def value(self):
        raise NotImplementedError("Accumulator should be subclassed")


class Average(Accumulator_):
    def __init__(self, plot_title=None, **kwargs):
        super(Average, self).__init__(plot_title, **kwargs)

    @property
    def value(self):
        return self._avg


class Sum(Accumulator_):
    def __init__(self, plot_title=None, **kwargs):
        super(Sum, self).__init__(plot_title, **kwargs)

    @property
    def value(self):
        return self._avg * self._total_weight


class Maximum(Base):
    def __init__(self, plot_title=None, **kwargs):
        super(Maximum, self).__init__(plot_title, **kwargs)
        self.chart_x_axis = 'time'
        self.chart_y_axis = ''

        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)
        self.reset()

    def reset(self):
        self._val = -np.inf
        self.hooks_on_new_max = ()
        return self

    def _update(self, val, n=None):
        val = float(val)
        if val > self._val:
            self._val = val
            for hook in self.hooks_on_new_max:
                hook()
                
        self.channel.update(self.time, self.value)
        
    def hook_on_new_max(self, hook):
        self.hooks_on_new_max += (hook,)

    @property
    def value(self):
        return self._val


class Minimum(Base):
    def __init__(self, plot_title=None, **kwargs):
        super(Minimum, self).__init__(plot_title, **kwargs)
        self.chart_x_axis = 'time'
        self.chart_y_axis = ''

        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)
        self.reset()

    def reset(self):
        self._val = np.inf
        self.hooks_on_new_min = ()
        return self

    def _update(self, val, n=None):
        val = float(val)
        if val < self._val:
            self._val = val
            for hook in self.hooks_on_new_min:
                hook()

        self.channel.update(self.time, self.value)

    def hook_on_new_min(self, hook):
        self.hooks_on_new_min += (hook,)

    @property
    def value(self):
        return self._val



# -*- coding: UTF-8 -*-
# @Time    : 2020/8/13 7:50 下午
# @File    : __init__.py.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from torch import nn
import torch
from antvis.client.mlogger.metric.base import *
import numpy as np
import uuid


class Image(Base):
    def __init__(self, plot_title, **kwargs):
        Base.__init__(self, plot_title, 'complex', **kwargs)
        self.channel =\
            mlogger.getEnv().create_channel(str(uuid.uuid4()),
                                            channel_type='IMAGE',
                                            **self.channel_config)

    def update(self, x):
        # tensor NCHW
        if len(x.shape) == 4 and x.shape[1] == 3 and x.dtype == torch.uint8:
            data = x.detach().cpu().data.numpy()
            for index in range(data.shape[0]):
                super(Image, self).update(data[index].transpose((1, 2, 0)))
        else:
            print('Only support channel = 3 or channel = 4, and dtype=torch.uint8.')

    @property
    def value(self):
        return self._val

    def _update(self, val):
        if type(val) == list:
            val = np.array(val)

        if type(val) != np.ndarray:
            print('image logger dont support non numpy.ndarray data')
            raise NotImplementedError

        assert (len(val.shape) == 2 or len(val.shape) == 3)
        if len(val.shape) == 3:
            assert (val.shape[2] == 3)

        self._val = val
        self.channel.update(self.time, self.value)


class Histogram(Base):
    def __init__(self, plot_title, **kwargs):
        Base.__init__(self, plot_title, 'complex', **kwargs)
        self.channel = \
            mlogger.getEnv().create_channel(str(uuid.uuid4()),
                                            channel_type='HISTOGRAM',
                                            **self.channel_config)
        self.multi_channels = [self.channel]

    def update(self, x):
        # NCHW
        if x is not None:
            data = x.detach().cpu().data.numpy()
            super(Histogram, self).update(data)

    @property
    def value(self):
        return self._val

    def _update(self, val):
        # 基于Batch维度进行展开分析
        if len(val.shape) == 1:
            # 单通道数据
            self.multi_channels[0].update(self.time, val)
        else:
            # 多通道数据
            if val.shape[0] > len(self.multi_channels):
                # 将新增通道加入图表
                channel_num = len(self.multi_channels)
                for index in range(val.shape[0] - channel_num):
                    new_channel = \
                        mlogger.getEnv().create_channel('%s-%d'%(self.channel.channel_name, index+channel_num),
                                                        channel_type='HISTOGRAM',
                                                        **self.channel_config)
                    self.chart.bind_channel(new_channel)
                    self.multi_channels.append(new_channel)

            for index in range(val.shape[0]):
                self.multi_channels[index].update(self.time, val[index])

        self._val = val


class Simple(Base):
    def __init__(self, plot_title, **kwargs):
        Base.__init__(self, plot_title, **kwargs)
        self.chart_x_axis = 'time'
        self.chart_y_axis = ''

        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)

    def update(self, x):
        super(Simple, self).update(x.detach().cpu().item())

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

    def __init__(self, plot_title, **kwargs):
        Base.__init__(self, plot_title, **kwargs)
        self.chart_x_axis = 'time'
        self.chart_y_axis = ''

        self.channel = \
            mlogger.getEnv().create_channel(str(uuid.uuid4()),
                                            channel_type='LINE',
                                            **self.channel_config)
        self._avg = None

    def reset(self):
        self._avg = 0
        self._total_weight = 0
        return self

    def _update(self, val, weighting=1):
        if self._avg is None:
            self.reset()

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

    def update(self, x):
        super(Accumulator_, self).update(x.detach().cpu().item())
        return x


class Average(Accumulator_):
    def __init__(self, plot_title, **kwargs):
        Accumulator_.__init__(self, plot_title, **kwargs)

    @property
    def value(self):
        return self._avg


class Sum(Accumulator_):
    def __init__(self, plot_title, **kwargs):
        Accumulator_.__init__(self, plot_title, **kwargs)

    @property
    def value(self):
        if self._avg is None:
            return None

        return self._avg * self._total_weight


class Maximum(Base):
    def __init__(self, plot_title, **kwargs):
        Base.__init__(self, plot_title, **kwargs)

        self.chart_x_axis = 'time'
        self.chart_y_axis = ''

        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)
        self._val = None

    def reset(self):
        self._val = -np.inf
        self.hooks_on_new_max = ()
        return self

    def _update(self, val, n=None):
        if self._val is None:
            self.reset()

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

    def update(self, x):
        super(Maximum, self).update(x.detach().cpu().item())


class Minimum(Base):
    def __init__(self, plot_title, **kwargs):
        Base.__init__(self, plot_title, **kwargs)

        self.chart_x_axis = 'time'
        self.chart_y_axis = ''

        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)
        self._val = None

    def reset(self):
        self._val = np.inf
        self.hooks_on_new_min = ()
        return self

    def _update(self, val, n=None):
        if self._val is None:
            self.reset()

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

    def update(self, x):
        super(Minimum, self).update(x.detach().cpu().item())
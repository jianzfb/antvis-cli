# -*- coding: UTF-8 -*-
# @Time    : 2020/7/23 6:10 下午
# @File    : __init__.py.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from antvis.client.mlogger.metric.base import *
import psutil
import uuid
import re
import os


class CPU(Base):
    def __init__(self, plot_title, **kwargs):
        plot_title = 'monitor/%s'%plot_title
        super(CPU, self).__init__(plot_title, **kwargs)
        self.chart_x_axis = 'time'
        self.chart_y_axis = 'percent'

        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)
        self.channel_min = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)
        self.channel_max = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)

        self.reset()

    @property
    def name(self):
        return self.channel.channel_name

    @name.setter
    def name(self, val):
        self.channel.channel_name = '%s/avg' % val
        self.channel_min.channel_name = '%s/min' % val
        self.channel_max.channel_name = '%s/max' % val

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
        self.chart.bind_channel(self.channel_min)
        self.chart.bind_channel(self.channel_max)

    @property
    def value(self):
        return self._avg

    def reset(self):
        self._avg = 0
        self._max_val = -np.inf
        self._min_val = np.inf
        self._total_weight = 0
        return self

    def _update(self, *args, **kwargs):
        # 获取cpu占用率
        val = psutil.cpu_percent(0)

        # 更新
        r = self._total_weight / (1.0 + self._total_weight)
        self._avg = r * self._avg + (1 - r) * val
        self._total_weight += 1.0

        if val > self._max_val:
            self._max_val = val
        if val < self._min_val:
            self._min_val = val

        self.channel.update(self.time, self._avg)
        self.channel_min.update(self.time, self._min_val)
        self.channel_max.update(self.time, self._max_val)


class Memory(Base):
    def __init__(self, plot_title, **kwargs):
        plot_title = 'monitor/%s' % plot_title
        super(Memory, self).__init__(plot_title, **kwargs)
        self.chart_x_axis = 'time'
        self.chart_y_axis = 'percent'

        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)
        self.channel_min = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)
        self.channel_max = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)

        self.reset()

    @property
    def name(self):
        return self.channel.channel_name

    @name.setter
    def name(self, val):
        self.channel.channel_name = '%s/avg' % val
        self.channel_min.channel_name = '%s/min' % val
        self.channel_max.channel_name = '%s/max' % val

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
        self.chart.bind_channel(self.channel_min)
        self.chart.bind_channel(self.channel_max)

    @property
    def value(self):
        return self._avg

    def reset(self):
        self._avg = 0
        self._max_val = -np.inf
        self._min_val = np.inf
        self._total_weight = 0
        return self

    def _update(self, *args, **kwargs):
        # 获取内存占用率
        val = psutil.virtual_memory().percent

        # 更新
        r = self._total_weight / (1.0 + self._total_weight)
        self._avg = r * self._avg + (1 - r) * val
        self._total_weight += 1.0

        if val > self._max_val:
            self._max_val = val
        if val < self._min_val:
            self._min_val = val

        self.channel.update(self.time, self._avg)
        self.channel_min.update(self.time, self._min_val)
        self.channel_max.update(self.time, self._max_val)


class GPU(Base):
    def __init__(self, plot_title, **kwargs):
        plot_title = 'monitor/%s' % plot_title
        super(GPU, self).__init__(plot_title, **kwargs)
        self.chart_x_axis = 'time'
        self.chart_y_axis = 'percent'

        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)
        self.channel_min = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)
        self.channel_max = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)

        self.reset()

    @property
    def name(self):
        return self.channel.channel_name

    @name.setter
    def name(self, val):
        self.channel.channel_name = '%s/avg' % val
        self.channel_min.channel_name = '%s/min' % val
        self.channel_max.channel_name = '%s/max' % val

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
        self.chart.bind_channel(self.channel_min)
        self.chart.bind_channel(self.channel_max)

    @property
    def value(self):
        return self._avg

    def reset(self):
        self._avg = 0
        self._max_val = -np.inf
        self._min_val = np.inf
        self._total_weight = 0
        return self

    def get_gpu_percent(self):
        try:
            p = os.popen('nvidia-smi')
            content = p.read()
            p.close()
            if content == '':
                return 0.0

            gpu_percent_list = re.findall(r"[0-9]*%", content)
            vv = []
            for g_v in gpu_percent_list:
                vv.append(float(g_v[:-1]))

            value = np.mean(np.array(vv))
            value = float(value)
            return value
        except:
            return 0.0

    def _update(self, *args, **kwargs):
        # 获取内存占用率
        val = self.get_gpu_percent()

        # 更新
        r = self._total_weight / (1.0 + self._total_weight)
        self._avg = r * self._avg + (1 - r) * val
        self._total_weight += 1.0

        if val > self._max_val:
            self._max_val = val
        if val < self._min_val:
            self._min_val = val

        self.channel.update(self.time, self._avg)
        self.channel_min.update(self.time, self._min_val)
        self.channel_max.update(self.time, self._max_val)


class GPUMemory(Base):
    def __init__(self, plot_title, **kwargs):
        plot_title = 'monitor/%s' % plot_title
        super(GPUMemory, self).__init__(plot_title, **kwargs)
        self.chart_x_axis = 'time'
        self.chart_y_axis = 'MB'

        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', **self.channel_config)
        self.channel_min = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE',
                                                           **self.channel_config)
        self.channel_max = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE',
                                                           **self.channel_config)

        self.reset()

    @property
    def name(self):
        return self.channel.channel_name

    @name.setter
    def name(self, val):
        self.channel.channel_name = '%s/avg' % val
        self.channel_min.channel_name = '%s/min' % val
        self.channel_max.channel_name = '%s/max' % val

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
        self.chart.bind_channel(self.channel_min)
        self.chart.bind_channel(self.channel_max)

    @property
    def value(self):
        return self._avg

    def reset(self):
        self._avg = 0
        self._max_val = -np.inf
        self._min_val = np.inf
        self._total_weight = 0
        return self

    def get_video_memory(self):
        try:
            p = os.popen('nvidia-smi')
            content = p.read()
            p.close()
            if content == '':
                return 0.0

            gpu_percent_list = re.findall(r"[0-9]*0MiB", content)
            vv = []
            for g_v in gpu_percent_list:
                vv.append(float(g_v[:-3]))

            value = np.mean(np.array(vv))
            value = float(value)
            return value
        except:
            return 0.0

    def _update(self, *args, **kwargs):
        # 获取内存占用率
        val = self.get_video_memory()

        # 更新
        r = self._total_weight / (1.0 + self._total_weight)
        self._avg = r * self._avg + (1 - r) * val
        self._total_weight += 1.0

        if val > self._max_val:
            self._max_val = val
        if val < self._min_val:
            self._min_val = val

        self.channel.update(self.time, self._avg)
        self.channel_min.update(self.time, self._min_val)
        self.channel_max.update(self.time, self._max_val)

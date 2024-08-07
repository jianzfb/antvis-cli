# -*- coding: UTF-8 -*-
# @Time    : 2020-06-30 13:37
# @File    : __init__.py.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

from antvis.client.mlogger.metric.base import *
from antvis.client.dashboard import *
from antvis.client import mlogger
import time
import logging


class Image(Base):
    def __init__(self, plot_title, **kwargs):
        super(Image, self).__init__(plot_title, 'complex', **kwargs)
        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='IMAGE', **self.channel_config)
        
    @property
    def value(self):
        return self._val
    
    def _update(self, val, x=None):
        # only support HWC, HW
        if type(val) == list:
            val = np.array(val)

        if type(val) != np.ndarray:
            logging.error('Image logger dont support non numpy.ndarray data')
            raise NotImplementedError

        assert(len(val.shape) == 2 or len(val.shape) == 3)
        if len(val.shape) == 3:
            assert(val.shape[2] == 3)

        if 'float' in str(val.dtype):
            if val.max() <= 1:
                val = val * 255
            val = np.uint8(val)
        assert ('uint8' in str(val.dtype))

        self._val = val
        if x is None:
            self.channel.update(self.time, self.value)
        else:
            self.channel.update((float)(x), self.value)

    def _get(self, data):
        for x, y in zip(data['x'], data['y']):
            r = requests.get(y, stream=True)
            with open('./%s.png'%(str(x)), "wb") as pdf:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        pdf.write(chunk)
        return data


class Histogram(Base):
    def __init__(self, plot_title, **kwargs):
        super(Histogram, self).__init__(plot_title, 'complex', **kwargs)
        
        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='HISTOGRAM', **self.channel_config)
        
    @property
    def value(self):
        return self._val
    
    def _update(self, val, x=None):
        self._val = val
        if x is None:
            self.channel.update(self.time, self.value)
        else:
            self.channel.update((float)(x), self.value)


class Bar(Base):
    def __init__(self, plot_title, **kwargs):
        super(Bar, self).__init__(plot_title, 'complex', **kwargs)

        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='BAR',
                                                       **self.channel_config)

    @property
    def value(self):
        return self._val

    def _update(self, x,y):
        self._val = (x,y)
        self.channel.update(x, y)


class Heatmap(Base):
    def __init__(self, plot_title, **kwargs):
        super(Heatmap, self).__init__(plot_title, 'complex', **kwargs)
        
        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='IMAGE', **self.channel_config)

    @property
    def value(self):
        return self._val
    
    def _update(self, val):
        if type(val) != np.ndarray:
            val = np.array(val)
        
        assert(len(val.shape) == 2)
        if self.chart.chart_x_axis == '':
            self.chart.chart_x_axis = ','.join([str(i) for i in range(val.shape[0])])
            
        if self.chart.chart_y_axis == '':
            self.chart.chart_y_axis = ','.join([str(i) for i in range(val.shape[1])])

        val = val.astype(np.float32)
        val = val / np.max(val)
        val = val * 255
        val = val.astype(np.uint8)
        self._val = val
        self.channel.update(self.time, self.value)

        
class Svg(Base):
    def __init__(self, plot_title, **kwargs):
        super(Svg, self).__init__(plot_title, 'complex', **kwargs)

        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='SVG', **self.channel_config)

    @property
    def value(self):
        return self._val

    def _update(self, val):
        assert(type(val) == str)
        self._val = val
        self.channel.update(self.time, self.value)


class Text(Base):
    def __init__(self, plot_title, **kwargs):
        super(Text, self).__init__(plot_title, 'complex', **kwargs)
        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='TEXT', **self.channel_config)

    @property
    def value(self):
        return self._val

    def _update(self, val):
        if type(val) != str:
            val = str(val)
            
        self._val = val
        self.channel.update(self.time, self.value)

    def _timestamp(self):
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        return time_str

    def info(self, val):
        self.update("{} [INFO]\t{}".format(self._timestamp(), val))

    def debug(self, val):
        self.update("{} [DEBUG]\t{}".format(self._timestamp(), val))

    def warn(self, val):
        self.update("{} [WARN]\t{}".format(self._timestamp(), val))


class Table(Base):
    def __init__(self, plot_title, **kwargs):
        super(Table, self).__init__(plot_title, 'complex', **kwargs)

        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='TABLE', **self.channel_config)

    @property
    def value(self):
        return self._val

    def _update(self, *args, **kwargs):
        self.channel.update(self.time, self.value)
    
    def __setattr__(self, key, value):
        if not key.startswith('r'):
            return super(Table, self).__setattr__(key, value)
        
        if len(key) != 4:
            return
        r,i,c,j = key
        if r!='r' or c!='c':
            return
        
        i = int(i)
        j = int(j)
        if i < 0 or j < 0:
            raise NotImplementedError
        
        if self._val is None or len(self._val) == 0:
            self._val = [['' for jj in range(j+1)] for ii in range(i+1)]
        
        if len(self._val) < (i+1):
            for _ in range((i+1) - len(self._val)):
                self._val.append(['' for jj in range(len(self._val[0]))])
        
        if len(self._val[0]) < (j+1):
            for r_index in range(len(self._val)):
                self._val[r_index].extend(['' for jj in range((j+1) - len(self._val[r_index]))])
        
        self._val[i][j] = value


class Scatter(Base):
    def __init__(self, plot_title, is_series=True, **kwargs):
        super(Scatter, self).__init__(plot_title, 'complex', **kwargs)
        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='SCATTER', time_series=is_series, **self.channel_config)
        self.is_series = is_series

    @property
    def value(self):
        return self._val

    def _update(self, val, x=None):
        if type(val) == list:
            val = np.array(val)

        if type(val) != np.ndarray:
            # 标量
            val = np.array([val])

        if len(val.shape) == 2:
            assert (not self.is_series)
            # val: 2xN, 第0行标识x的值，第1行标识y的值
            assert (val.shape[0] == 2 or val.shape[1] == 2)
            if val.shape[0] == 2:
                val = val.tolist()
            else:
                val = np.transpose(val)
                val = val.tolist()

            self._val = val
            x, y = val
            self.channel.update(x, y)
        else:
            val = val.tolist()
            if x is None:
                assert (len(val) == 1)
                if self.is_series:
                    self.channel.update(self.time, val[0])
                else:
                    self.channel.update([self.time], val)
            else:
                if type(x) != list and type(x) != np.ndarray:
                    x = [x]
                elif type(x) == np.ndarray:
                    assert (x.ndim == 1)
                    x = x.tolist()

                if self.is_series:
                    self.channel.update(x[0], val[0])
                else:
                    assert (len(val) == len(x))
                    self.channel.update(x, val)


class Line(Base):
    def __init__(self, plot_title, is_series=True, **kwargs):
        super(Line, self).__init__(plot_title, 'complex', **kwargs)
        self.channel = mlogger.getEnv().create_channel(str(uuid.uuid4()), channel_type='LINE', time_series=is_series, **self.channel_config)
        self.is_series = is_series

    @property
    def value(self):
        return self._val

    def _update(self, val, x=None):
        if type(val) == list:
            val = np.array(val)

        if type(val) != np.ndarray:
            # 标量
            val = np.array([val])

        if len(val.shape) == 2:
            assert(not self.is_series)
            # val: 2xN, 第0行标识x的值，第1行标识y的值
            assert (val.shape[0] == 2 or val.shape[1] == 2)
            if val.shape[0] == 2:
                val = val.tolist()
            else:
                val = np.transpose(val)
                val = val.tolist()

            self._val = val
            x, y = val
            self.channel.update(x, y)
        else:
            val = val.tolist()
            if x is None:
                assert(len(val) == 1)
                if self.is_series:
                    self.channel.update(self.time, val[0])
                else:
                    self.channel.update([self.time], val)
            else:
                if type(x) != list and type(x) != np.ndarray:
                    x = [x]
                elif type(x) == np.ndarray:
                    assert(x.ndim == 1)
                    x = x.tolist()

                if self.is_series:
                    self.channel.update(x[0], val[0])
                else:
                    assert(len(val) == len(x))
                    self.channel.update(x, val)

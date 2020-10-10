# encoding=utf-8
# Time: 8/28/17
# File: job.py
# Author: jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

import uuid
import threading
import numpy as np
import re
import copy
import sys
import scipy.misc
import base64
import os
import logging
import requests
from antvis.utils.utils import *
from antvis.utils.encode import *
import json
from PIL import Image


PYTHON_VERSION = sys.version_info[0]
if PYTHON_VERSION == 2:
    import Queue as queue
elif PYTHON_VERSION == 3:
    import queue as queue


class Chart(object):
  def __init__(self, title="chart", x_axis="x", y_axis="y", dashboard=None):
    self.chart_title = title
    self.chart_x_axis = x_axis
    self.chart_y_axis = y_axis
    self.chart_channels = []
    self.chart_map = {}
    self.dashboard = dashboard

  @property
  def uuid(self):
    if self.dashboard.experiment_stage not in self.chart_map:
      self.chart_map[self.dashboard.experiment_stage] = unicode(uuid.uuid1()) if PYTHON_VERSION == 2 else str(uuid.uuid1())
    return self.chart_map[self.dashboard.experiment_stage]

  @property
  def title(self):
    return self.chart_title

  @property
  def x_axis(self):
    return self.chart_x_axis

  @x_axis.setter
  def x_axis(self, val):
    self.chart_x_axis = val

  @property
  def y_axis(self):
    return self.chart_y_axis

  @y_axis.setter
  def y_axis(self, val):
    self.chart_y_axis = val

  @property
  def channels_num(self):
    return len(self.chart_channels)

  def bind_channel(self, channel):
    if len(self.chart_channels) != 0:
      assert(channel.channel_type == self.chart_channels[0].channel_type)

    # 检查是否支持multi-channel
    if len(self.chart_channels) > 0 and channel.channel_type not in ['SCATTER', 'LINE', 'HISTOGRAM', 'BAR', 'TEXT', 'IMAGE']:
      logging.error('channel type %s not support multi-channel in one chart'%channel.channel_type)
      raise NotImplementedError
      
    channel.id = len(self.chart_channels)
    channel.chart = self
    self.chart_channels.append(channel)
    
  
class Channel(object):
  def __init__(self, channel_name=None, channel_type=None, channel_job=None, time_series=True, **channel_params):
    self.channel_id = -1
    self.channel_name = channel_name
    self.channel_type = channel_type
    self.channel_chart = None
    self.channel_job = channel_job
    self.channel_params = channel_params
    self.time_series = time_series
    assert(self.channel_type in ["IMAGE", "SVG", "SCATTER", "HISTOGRAM", "BAR", "LINE", "TEXT", "TABLE", "HEATMAP"])

  @property
  def params(self):
    return self.channel_params

  @property
  def chart(self):
    return self.channel_chart
  
  @chart.setter
  def chart(self, val):
    self.channel_chart = val

  @property
  def id(self):
    return self.channel_id
  
  @id.setter
  def id(self, val):
    self.channel_id = val

  @property
  def name(self):
    return self.channel_name
  
  @name.setter
  def name(self, val):
    self.channel_name = val

  def transform_to_svg(self, data):
    x,y = data
    return x,y
  
  def transform_to_image(self, data):
    data_x, data_y = data
    try:
      data_x = float(data_x)
    except:
      logging.error("Channel X Must be Scalar Data")
      return None

    try:
      if len(data_y.shape) != 2 and len(data_y.shape) != 3:
        logging.error("Channel Y Must be 2 or 3 Dimension")
        return None
      if len(data_y.shape) == 3:
        if data_y.shape[2] != 3:
          logging.error("Channel Y Must Possess 3 or 1 Channels")
          return None

      if data_y.dtype == np.uint8:
        return (data_x, base64.b64encode(png_encode(data_y)).decode('utf-8'))

      max_val = np.max(data_y.flatten())
      min_val = np.min(data_y.flatten())
      if len(data_y.shape) == 3:
        data_y = ((data_y - np.tile(min_val, (1,1,3))) / np.tile(max_val, (1,1,3))) * 255
        data_y = data_y.astype(np.uint8)
      else:
        data_y = (data_y - min_val) / max_val * 255
        data_y = data_y.astype(np.uint8)

      return (data_x, base64.b64encode(png_encode(data_y)).decode('utf-8'))
    except:
      logging.error("Channel Y Must be Numpy Array")

  def transform_to_scatter(self, data):
    data_x, data_y = data
    try:
      data_x = float(data_x)
    except:
      logging.error("X Must be Scalar Data")
      return None

    if type(data_y) == dict:
      try:
        data_y['y'] = float(data_y['y'])
        data_y['size'] = float(data_y['size'])
        return (data_x, data_y)
      except:
        logging.error("Y mean and var must be Scalar Data")

    try:
      data_y = float(data_y)
    except:
      logging.error("Y Must be Scalar Data")
    return (data_x, {'y': data_y, 'size': 10})
  
  def transform_to_line(self, data):
    data_x, data_y = data
    try:
      data_x = float(data_x)
    except:
      logging.error("X Must be Scalar Data")
      return None
    
    if type(data_y) == dict:
      try:
        data_y['mean'] = float(data_y['mean'])
        data_y['var'] = float(data_y['var'])
        return (data_x, data_y)
      except:
        logging.error("Y mean and var must be Scalar Data")
    
    try:
      data_y = float(data_y)
    except:
      logging.error("Y Must be Scalar Data")
    return (data_x, {'mean': data_y, 'var': -1.0})

  def transform_to_bar(self, data):
    data_x, data_y = data
    if type(data_x) != list or type(data_y) != list:
      return None

    if len(data_x) != len(data_y):
      return None

    return data_x, data_y

  def transform_to_histogram(self, data):
    data_x, data_y = data
    try:
      data_x = float(data_x)
    except:
      logging.error("Channel X Must be Scalar Data")
      return None
    
    try:
      data_y = np.array(data_y)
      data_y = data_y.flatten()
      bins = 10 # default bins
      if "BINS" in self.params:
        bins = self.params['BINS']
      
      data_y = np.histogram(data_y, bins)
    except:
      logging.error("Channel Y Must be Numpy Array")
    return (data_y[1].tolist(),data_y[0].tolist())

  def update(self, x=0, y=0):
    # {"CHART", (chart_id, chart_title,...)}
    x = copy.deepcopy(x)
    y = copy.deepcopy(y)

    data_vis_type = self.channel_type
    if self.channel_type == 'HISTOGRAM':
      data_vis_type = 'BAR'

    data = {"CHART": {"chart_uuid": self.chart.uuid,
                               "chart_title": self.chart.title,
                               "chart_x_axis": self.chart.x_axis,
                               "chart_y_axis": self.chart.y_axis,
                               "chart_type": data_vis_type,
                               "chart_channels": self.chart.channels_num,
                               "channel_id": self.id,
                               "channel_type": data_vis_type,
                               "channel_name": self.channel_name,
                               "channel_time_series": self.time_series,
                               "channel_data": []}}
    
    if self.channel_type == 'IMAGE':
      xxyy = self.transform_to_image((x,y))
      if xxyy is None:
        return
      
      x,y = xxyy
      data['CHART']['channel_data'].append({'x': x, 'y': y})
    elif self.channel_type == 'SVG':
      xxyy = self.transform_to_svg((x,y))
      if xxyy is None:
        return
      
      x,y = xxyy
      data['CHART']['channel_data'].append({'x': x, 'y': y})
    elif self.channel_type == 'SCATTER':
      if not self.time_series:
        data['CHART']['channel_data'] = []
        for x, y in zip(x, y):
          xxyy = self.transform_to_scatter((x,y))
          if xxyy is None:
            continue

          data['CHART']['channel_data'].append({'x': xxyy[0], 'y': xxyy[1]})

        self.channel_job.cache(data)
        return

      xxyy = self.transform_to_scatter((x,y))
      if xxyy is None:
        return
    
      x,y = xxyy
      data['CHART']['channel_data'].append({'x': x, 'y': y})
    elif self.channel_type == 'LINE':
      if not self.time_series:
        data['CHART']['channel_data'] = []
        for x, y in zip(x, y):
          xxyy = self.transform_to_scatter((x,y))
          if xxyy is None:
            continue

          data['CHART']['channel_data'].append({'x': xxyy[0], 'y': xxyy[1]})

        self.channel_job.cache(data)
        return

      xxyy = self.transform_to_line((x, y))
      if xxyy is None:
        return
  
      x, y = xxyy
      data['CHART']['channel_data'].append({'x': x, 'y': y})
    elif self.channel_type == 'HISTOGRAM':
      xxyy = self.transform_to_histogram((x, y))
      if xxyy is None:
        return
      
      x,y = xxyy
      data['CHART']['channel_data'].append({'x': x, 'y': y})
    elif self.channel_type == 'BAR':
      xxyy = self.transform_to_bar((x, y))
      if xxyy is None:
        return

      x, y = xxyy
      data['CHART']['channel_data'].append({'x': x, 'y': y})
    elif self.channel_type == 'HEATMAP':
      if type(y) == np.ndarray:
        y = y.tolist()
      
      if type(y) != list:
        return

      data['CHART']['channel_data'].append({'x': x, 'y': y})
    else:
      data['CHART']['channel_data'].append({'x': x, 'y': y})
    
    # push to cache
    self.channel_job.cache(data)


class ExitSig(object):
  pass


class Job(threading.Thread):
  def __init__(self, dashboard=None, cache_max_size=100):
    super(Job, self).__init__()
    self.data_queue = queue.Queue()
    self.dashboard = dashboard
    self.pid = str(os.getpid())
    self.charts = []
    self.cache_data = []
    self.cache_max_size = cache_max_size
    self.dashboard_ip = self.dashboard.dashboard_ip
    self.dashboard_port = self.dashboard.dashboard_port
    self.dashboard_prefix = 'http'
  
  def create_channel(self, channel_name, channel_type, **kwargs):
    return Channel(channel_name, channel_type, self, **kwargs)

  def create_chart(self, chart_channels, chart_title, chart_x_axis="x", chart_y_axis="y", **kwargs):
    chart = Chart(chart_title, chart_x_axis, chart_y_axis, dashboard=self.dashboard)
    self.charts.append(chart)
    channel_type = None
    for cc in chart_channels:
      if channel_type is None:
        channel_type = cc.channel_type
      else:
        # assert channel has the same type
        assert(channel_type == cc.channel_type)

      chart.bind_channel(cc)
    return chart
  
  def cache(self, data):
    if self.dashboard.experiment_name is not None:
      # fill context data
      context_data = {'APP_TIME': self.dashboard.launch_time,
                      'APP_NOW_TIME': timestamp(),
                      'APP_SERVER': self.dashboard.server,
                      'APP_EXPERIMENT_NAME': self.dashboard.experiment_name,
                      'APP_EXPERIMENT_UUID': self.dashboard.experiment_uuid,
                      'APP_HYPER_PARAMETER': self.dashboard.experiment_hyper_parameter,
                      'APP_STAGE': self.dashboard.experiment_stage}
  
      data.update(context_data)
      
      # cache data
      self.cache_data.append(data)
      
      # auto triger update data
      if len(self.cache_data) > self.cache_max_size:
        self.update()
  
  def update(self):
    if len(self.cache_data) > 0:
      self.data_queue.put(self.cache_data)
      self.cache_data = []
  
  def exit(self):
    self.data_queue.put(ExitSig())
  
  def run(self):
    while True:
      # 0.step get data
      data = self.data_queue.get()

      # 1.step is exit signal
      if type(data) == ExitSig:
        break

      # 2.step data is none or empty
      if data is None or len(data) == 0:
          continue
      
      # 3.step merge data by chart uuid
      data_package = {'CHART': {}, 'APP_STAGE': data[0]['APP_STAGE']}
      for item in data:
        if 'TAG' in item:
          if 'TAG' not in data_package:
            data_package["TAG"] = {}
          data_package['TAG'].update(item['TAG'])
        elif 'CHART' in item:
          chart_uuid = item['CHART']['chart_uuid']
          channel_id = item['CHART']['channel_id']

          if chart_uuid not in data_package['CHART']:
            data_package['CHART'][chart_uuid] = {}
            data_package['CHART'][chart_uuid].update(item['CHART'])
            data_package['CHART'][chart_uuid].pop('channel_id')
            data_package['CHART'][chart_uuid].pop('channel_type')
            data_package['CHART'][chart_uuid].pop('channel_name')
            data_package['CHART'][chart_uuid].pop('channel_data')
            data_package['CHART'][chart_uuid]['channels'] = {}

          if channel_id not in data_package['CHART'][chart_uuid]['channels']:
            data_package['CHART'][chart_uuid]['channels'][channel_id] = None

          if data_package['CHART'][chart_uuid]['channels'][channel_id] is None:
            data_package['CHART'][chart_uuid]['channels'][channel_id] = {}
            data_package['CHART'][chart_uuid]['channels'][channel_id]['channel_id'] = item['CHART']['channel_id']
            data_package['CHART'][chart_uuid]['channels'][channel_id]['channel_type'] = item['CHART']['channel_type']
            data_package['CHART'][chart_uuid]['channels'][channel_id]['channel_name'] = item['CHART']['channel_name']
            data_package['CHART'][chart_uuid]['channels'][channel_id]['channel_data'] = item['CHART']['channel_data']
            data_package['CHART'][chart_uuid]['channels'][channel_id]['channel_time_series'] = item['CHART']['channel_time_series']
          else:
            if item['CHART']['channel_time_series']:
              data_package['CHART'][chart_uuid]['channels'][channel_id]['channel_data'].extend(item['CHART']['channel_data'])
            else:
              data_package['CHART'][chart_uuid]['channels'][channel_id]['channel_data'] = item['CHART']['channel_data']

          if data_package['CHART'][chart_uuid]['chart_channels'] < len(data_package['CHART'][chart_uuid]['channels']):
            data_package['CHART'][chart_uuid]['chart_channels'] = len(data_package['CHART'][chart_uuid]['channels'])

      # 4.step remote call
      experiment_data = \
        {'experiment_name': self.dashboard.experiment_name,
         'experiment_uuid': self.dashboard.experiment_uuid,
         'experiment_data': json.dumps(data_package),
         'experiment_stage': data[0]['APP_STAGE'],
         'experiment_hyper_parameter': data[0]['APP_HYPER_PARAMETER']}
      
      if self.dashboard != None:
        self.dashboard.rpc.experiment.patch(**experiment_data)

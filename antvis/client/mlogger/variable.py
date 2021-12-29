# -*- coding: UTF-8 -*-
# @Time    : 2021/12/29 8:27 下午
# @File    : variable.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
import time
import sys
import logging


class Variable(object):
  env = None

  def __init__(self):
    pass

  def __setattr__(self, key, value):
    # 设置变量名称
    value.name = key
    super(Variable, self).__setattr__(key, value)


class _VarObj(object):
  def __init__(self, _type, default):
    self._name = None
    self._val = default         # 当前使用的值
    self._local_val = default   # 本地修改后的值
    self._type = _type

  @property
  def name(self):
    return self._name

  @name.setter
  def name(self, val):
    self._name = val

  def _update(self, val):
    raise NotImplementedError

  def set(self, val):
    self._update(val)

  def get(self):
    # 变量修改优先级：web > 本地
    response = Variable.env.dashboard.rpc.experiment.variable.get(
      experiment_uuid=Variable.env.dashboard.experiment_uuid,     # 实验uuid
      variable_name=self.name,                                # 变量名字
      variable_value=self._val,                               # 变量最新值
      variable_local_value=self._local_val,                   # 局部修改值
      variable_type=self._type                                # 变量类型
    )
    if 'status' in response and response['status'] == 'ERROR':
      logging.error("Couldnt get variable {} ".format(self.name))
      return None

    # 重置变量
    self._val = response['content']['variable_value']
    self._local_val = response['content']['variable_value']
    return self._val


class FloatVar(_VarObj):
  def __init__(self, default):
    super(FloatVar, self).__init__('float', float(default))

  def _update(self, val):
    if self._val == val:
      return False

    try:
      self._local_val = float(val)
      return True
    except:
      return False


class IntVar(_VarObj):
  def __init__(self, default):
    super(IntVar, self).__init__('int', int(default))

  def _update(self, val):
    if self._val == val:
      return False

    try:
      self._local_val = int(val)
      return True
    except:
      return False


class BoolVar(_VarObj):
  def __init__(self, default):
    super(BoolVar, self).__init__('bool', bool(default))

  def _update(self, val):
    if self._val == val:
      return False

    try:
      self._local_val = bool(val)
      return True
    except:
      return False


class StringVar(_VarObj):
  def __init__(self, default):
    super(StringVar, self).__init__('string', str(default))

  def _update(self, val):
    if self._val == val:
      return False

    try:
      self._local_val = str(val)
      return True
    except:
      return False


class TriggerVar(_VarObj):
  def __init__(self):
    super(TriggerVar, self).__init__('trigger', False)

  def waitting(self, timeout=None):
    current_time = time.time()
    is_trigger = False
    max_waiting_time = 2*24*60*60 if timeout is None else timeout
    while time.time() - current_time < max_waiting_time:
      response = Variable.env.dashboard.rpc.experiment.variable.get(
        experiment_uuid=Variable.env.dashboard.experiment_uuid,
        variable_name=self.name,                                # 变量名字
        variable_value=False,
        variable_local_value=False,
        variable_type=self._type                                # 变量类型
      )
      if 'status' in response and response['status'] == 'ERROR':
        logging.error("Couldnt get variable {} ".format(self.name))
        return

      self._val = response['content']['variable_value']
      if self._val:
        is_trigger = True
        break

      # 等待30s
      time.sleep(30)

    if not is_trigger:
      # 由于超时，退出
      sys.exit(-1)
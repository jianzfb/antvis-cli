# -*- coding: UTF-8 -*-
# @Time    : 2020-06-01 09:00
# @File    : __init__.py.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

import atexit
import sys
from . import mlogger
import logging
__exit_flag = False


def handle_exit():
  global __exit_flag
  if not __exit_flag:
    # project/experiment
    if mlogger.getEnv() is None or mlogger.getEnv().dashboard is None:
      return

    #
    project = mlogger.getEnv().dashboard.project
    experiment = mlogger.getEnv().dashboard.experiment_name

    if project is not None and experiment is not None:
      # 更新未上传数据
      mlogger.update()

      # 日志退出
      logging.info('Prepare exit {}/{} experiment logger'.format(project, experiment))
      mlogger.exit()

      # print log
      logging.info('Finish {}/{} experiment logger'.format(project, experiment))


def handle_exception(exc_type, exc_value, exc_traceback):
  global __exit_flag
  __exit_flag = True
  if mlogger.getEnv() is None or mlogger.getEnv().dashboard is None:
    return

  project = mlogger.getEnv().dashboard.project
  experiment = mlogger.getEnv().dashboard.experiment_name

  if project is not None and experiment is not None:
    # error
    mlogger.error()
    # print error info
    print(exc_traceback)
    # print log
    logging.error('Error {}/{} experiment logger'.format(project, experiment))


sys.excepthook = handle_exception
atexit.register(handle_exit)

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
import signal
import traceback
__exit_flag = False


def handle_exit():
  # 是否完成初始化
  if mlogger.getEnv() is None or mlogger.getEnv().dashboard is None:
    return

  # 项目名称/实验名称
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
  # print error info
  traceback.print_exception(exc_type, exc_value, exc_traceback)
  # 是否完成初始化
  if mlogger.getEnv() is None or mlogger.getEnv().dashboard is None:
    return

  # 项目名称/实验名称
  project = mlogger.getEnv().dashboard.project
  experiment = mlogger.getEnv().dashboard.experiment_name

  if project is not None and experiment is not None:
    # error
    mlogger.error()
    # print log
    logging.error('Error {}/{} experiment logger'.format(project, experiment))


sys.excepthook = handle_exception
atexit.register(handle_exit)
signal.signal(signal.SIGTERM, handle_exception)
signal.signal(signal.SIGINT, handle_exception)

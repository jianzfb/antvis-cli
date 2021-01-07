# -*- coding: UTF-8 -*-
# @Time    : 2020-06-01 09:00
# @File    : __init__.py.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

import atexit
import sys
import antvis.client.mlogger as mlogger

__exit_flag = False


def handle_exit():
  global __exit_flag
  if not __exit_flag:
    # project/experiment
    project = mlogger.getEnv().dashboard.project
    experiment = mlogger.getEnv().dashboard.experiment_name

    if project is not None and experiment is not None:
      # exit
      mlogger.exit()

      # print log
      print('finish {}/{} experiment logger'.format(project, experiment))


def handle_exception(exc_type, exc_value, exc_traceback):
  global __exit_flag
  __exit_flag = True

  project = mlogger.getEnv().dashboard.project
  experiment = mlogger.getEnv().dashboard.experiment_name

  if project is not None and experiment is not None:
    # error
    mlogger.error()
    # print error info
    print(exc_traceback)
    # print log
    print('error {}/{} experiment logger'.format(project, experiment))


sys.excepthook = handle_exception
atexit.register(handle_exit)

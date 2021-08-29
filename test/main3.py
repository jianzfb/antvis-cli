# -*- coding: UTF-8 -*-
# @Time    : 2021/1/3 8:45 下午
# @File    : main3.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
import antvis.client.mlogger as mlogger
import numpy as np
import time


if __name__ == "__main__":
  mlogger.config('59.110.164.237',
                 8080,
                 token='acee26bd077d4f55afa8dad3f5828fb2')
  project = 'you'
  experiment = 'jian10'
  mlogger.activate(project, experiment)

  # 测试实验标签获取
  print(mlogger.tag.learning_rate.get())
  print(mlogger.tag.batch_size.get())
  print(mlogger.tag.weight_decay.get())

  # 获得图表数据
  container_1 = mlogger.Container()
  container_1.growth_curve = mlogger.metric.Simple('growth')
  print(container_1.growth_curve.get())

  # 更新日志文件
  container_1.after = mlogger.FileLogger('after-1')
  container_1.before = mlogger.FileLogger('before-1')

  container_1.after.update('/Users/jian/Downloads/bdd79fec-1ad0-405f-bea9-557300b33993-db928c27-f234-463b-a073-81941824f701_1-200413093331.zip')
  container_1.before.update('/Users/jian/Downloads/character.jpg')
# -*- coding: UTF-8 -*-
# @Time    : 2021/10/7 6:18 下午
# @File    : example_native_api.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
import antvis.client.mlogger as mlogger
import numpy as np
import time

project = 'AA'
experiment = 'my_exp_3'

# 创建实验
mlogger.config(project, experiment, token='706cb1895fb84507b6fa4703bfbe3026')

# 添加实验标签
mlogger.tag.learning_rate = '0.01'
mlogger.tag.batch_size = '126'
mlogger.tag.optimizer = 'TYQ'
mlogger.tag.weight_decay = '0.0001'
mlogger.tag.alg = 'TVN'

xp = mlogger.Container()
xp.train = mlogger.Container()
xp.train.accuracy = mlogger.metric.Average('accuracy')
for j in range(10):
  xp.train.accuracy.update(j)

xp.test = mlogger.Container()
xp.test.show1 = mlogger.complex.Image("S")
xp.test.show2 = mlogger.complex.Image("S")
xp.test.show3 = mlogger.complex.Image("S")
xp.test.show4 = mlogger.complex.Image("S")

for index in range(10):
  data = np.random.random((255,255, 3))
  xp.test.show1.update(data)
  data = np.random.random((255,255, 3))
  xp.test.show2.update(data)
  data = np.random.random((255,255, 3))
  xp.test.show3.update(data)
  data = np.random.random((255,255, 3))
  xp.test.show4.update(data)
  mlogger.update()

  time.sleep(10)


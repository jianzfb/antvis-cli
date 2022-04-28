# -*- coding: UTF-8 -*-
# @Time    : 2022/1/16 10:04 下午
# @File    : coco_det_baseline.py.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
import antvis.client.mlogger as mlogger

import numpy as np
import time

project = 'AA'
experiment = 'efficientlite_0'

# 创建实验
mlogger.config(project, experiment, token='be5d805283254a1c97bf8acd546dcdd9', server='BASELINE')
xp = mlogger.Container()
xp.train = mlogger.Container()
# xp.train.loss_xy = mlogger.complex.Line('loss_xy', False)
# xp.train.loss_wh = mlogger.complex.Line('loss_wh', False)
# xp.train.loss_obj = mlogger.complex.Line('loss_obj', False)
# xp.train.loss_cls = mlogger.complex.Line('loss_cls', False)
xp.train.loss = mlogger.complex.Line('loss', False)
xp.train.lr = mlogger.complex.Line('lr', False)

loss=[]
learning_rate=[]
with open("./coco-det/EfficientLite0.log", 'r') as fp:
  line = fp.readline()
  line = line.strip()
  line_count = 0
  while True:
    line_count += 1
    if line_count <= 159:
      line = fp.readline()
      line = line.strip()
      continue

    # 5,6
    kkvv = line.split(' ')
    if len(kkvv) == 24:
      # 训练阶段日志
      pass
    

    for mi, mc in enumerate(kkvv):
      if mc.startswith('loss_xy:'):
        loss_xy.append((float)(kkvv[mi+1]))

      if mc.startswith('loss_wh'):
        loss_wh.append((float)(kkvv[mi+1]))

      if mc.startswith('loss_obj'):
        loss_obj.append((float)(kkvv[mi+1]))

      if mc.startswith('loss_cls'):
        loss_cls.append((float)(kkvv[mi+1]))

      if mc=='loss:':
        loss.append((float)(kkvv[mi+1]))

      if mc.startswith('learning_rate'):
        learning_rate.append((float)(kkvv[mi+1]))

    line = fp.readline()
    line = line.strip()
    if line == '':
      break


# xp.train.tt.update([j for j in range(50)], [j for j in range(50)])
xp.train.loss_xy.update(loss_xy, [j for j in range(len(loss_xy))])
xp.train.loss_wh.update(loss_wh, [j for j in range(len(loss_wh))])
xp.train.loss_obj.update(loss_obj, [j for j in range(len(loss_obj))])
xp.train.loss_cls.update(loss_cls, [j for j in range(len(loss_cls))])
xp.train.loss.update(loss, [j for j in range(len(loss))])
xp.train.lr.update(learning_rate, [j for j in range(len(learning_rate))])
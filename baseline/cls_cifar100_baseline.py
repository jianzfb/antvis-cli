# -*- coding: UTF-8 -*-
# @Time    : 2022/1/16 10:04 下午
# @File    : cls_baseline.py.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
import antvis.client.mlogger as mlogger

import numpy as np
import time

project = 'AA'
experiment = 'MobileNetV3_small'

# 创建实验
mlogger.config(project, experiment, token='6dab0a25878f43c7afe30881a85cf369', server='BASELINE')
xp = mlogger.Container()
xp.train = mlogger.Container()
xp.train.loss = mlogger.complex.Line('loss', False)
xp.train.lr = mlogger.complex.Line('lr', False)

xp.valid = mlogger.Container()
xp.valid.top_1 = mlogger.complex.Line('top-1', False)
xp.valid.top_5 = mlogger.complex.Line('top-5', False)

loss=[]
learning_rate=[]

top_1=[]
top_5=[]
with open("./cifar10-cls/log_train_MobileNetV3_small_x1_0_CIFAR10", 'r') as fp:
  line = fp.readline()
  line = line.strip()
  line_count = 0
  while True:
    line_count += 1
    if line_count < 178:
      line = fp.readline()
      line = line.strip()
      continue

    # 5,6
    line = line.replace('[', ' ')
    line = line.replace(']', ' ')
    line = line.replace('  ',' ')
    line = line.replace('   ', ' ')
    kkvv = line.split(' ')
    if 'Train' in line and 'CELoss' in line:
      # 训练阶段日志
      for mi, mc in enumerate(kkvv):
        if mc.startswith('loss'):
          loss.append((float)(kkvv[mi + 1][:-1]))

        if mc.startswith('lr'):
          learning_rate.append((float)(kkvv[mi + 1][:-1]))

    if'Eval' in line and 'Avg' in line:
      # ceshi
      for mi, mc in enumerate(kkvv):
        if mc.startswith('top1'):
          top_1.append((float)(kkvv[mi + 1][:-1]))

        if mc.startswith('top5'):
          top_5.append((float)(kkvv[mi + 1]))
      pass

    line = fp.readline()
    line = line.strip()
    if line == '':
      break

# loss = [t for ti,t in enumerate(loss) if ti % 1 == 1]
# learning_rate = [t for ti,t in enumerate(learning_rate) if ti % 1 == 1]
#

# top_1 = [t for ti,t in enumerate(top_1) if ti % 2 == 1]
# top_5 = [t for ti,t in enumerate(top_5) if ti % 2 == 1]
print(top_1)
xp.train.loss.update(loss, [j for j in range(len(loss))])
xp.train.lr.update(learning_rate, [j for j in range(len(learning_rate))])

xp.valid.top_1.update(top_1,[j for j in range(len(top_1))])
xp.valid.top_5.update(top_5,[j for j in range(len(top_5))])
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
experiment = 'faster_rcnn_r34_fpn_1x_coco'

# 创建实验
mlogger.config(project, experiment, token='be5d805283254a1c97bf8acd546dcdd9', server='BASELINE')
xp = mlogger.Container()
xp.train = mlogger.Container()
# xp.train.loss_xy = mlogger.complex.Line('loss_xy', False)
# xp.train.loss_wh = mlogger.complex.Line('loss_wh', False)
# xp.train.loss_obj = mlogger.complex.Line('loss_obj', False)
# xp.train.loss_cls = mlogger.complex.Line('loss_cls', False)
xp.train.loss_rpn_cls = mlogger.complex.Line('loss_rpn_cls', False)
xp.train.loss_rpn_reg = mlogger.complex.Line('loss_rpn_reg', False)
xp.train.loss_bbox_cls = mlogger.complex.Line('loss_bbox_cls', False)
xp.train.loss_bbox_reg = mlogger.complex.Line('loss_bbox_reg', False)
xp.train.loss = mlogger.complex.Line('loss', False)
xp.train.learning_rate = mlogger.complex.Line('learning_rate', False)

xp.valid = mlogger.Container()
xp.valid.mAP = mlogger.complex.Line('mAP', False)
xp.valid.mAR = mlogger.complex.Line('mAR', False)

loss_rpn_cls=[]
loss_rpn_reg=[]
loss_bbox_cls=[]
loss_bbox_reg=[]
loss=[]
learning_rate=[]

mAP=[]
mAR=[]
with open("./coco-det/faster_rcnn_r34_fpn_1x_coco.log", 'r') as fp:
  line = fp.readline()
  line = line.strip()
  line_count = 0
  while True:
    line_count += 1
    if line_count < 71:
      line = fp.readline()
      line = line.strip()
      continue

    # 5,6
    line = line.replace('  ',' ')
    kkvv = line.split(' ')
    if 'loss_rpn_cls' in line:
      # 训练阶段日志
      for mi, mc in enumerate(kkvv):
        if mc.startswith('loss_rpn_cls'):
          loss_rpn_cls.append((float)(kkvv[mi + 1]))
        if mc.startswith('loss_rpn_reg'):
          loss_rpn_reg.append((float)(kkvv[mi + 1]))

        if mc.startswith('loss_bbox_cls'):
          loss_bbox_cls.append((float)(kkvv[mi + 1]))

        if mc.startswith('loss_bbox_reg'):
          loss_bbox_reg.append((float)(kkvv[mi + 1]))

        if mc == 'loss' or mc == 'loss:':
          loss.append((float)(kkvv[mi + 1]))

        if mc.startswith('learning_rate'):
          learning_rate.append((float)(kkvv[mi + 1]))

    if 'Average Precision' in line and 'AP' in line and 'IoU=0.50:0.95' in line and 'all' in line and 'small' not in line:
      # ceshi
      mAP.append((float)(kkvv[-1]))

    if 'Average Recall' in line and 'AR' in line and 'IoU=0.50:0.95' in line and 'maxDets=100' in line and 'area=  all'in line:
      # ceshi
      mAR.append((float)(kkvv[-1]))

    line = fp.readline()
    line = line.strip()
    if line == '':
      break

loss_rpn_cls=[t for ti,t in enumerate(loss_rpn_cls) if ti % 5 == 1]
loss_rpn_reg=[t for ti,t in enumerate(loss_rpn_reg) if ti % 5 == 1]
loss_bbox_cls=[t for ti,t in enumerate(loss_bbox_cls) if ti % 5 == 1]
loss_bbox_reg=[t for ti,t in enumerate(loss_bbox_reg) if ti % 5 == 1]
loss=[t for ti,t in enumerate(loss) if ti % 5 == 1]
learning_rate=[t for ti,t in enumerate(learning_rate) if ti % 5 == 1]


xp.train.loss_rpn_cls.update(loss_rpn_cls, [j for j in range(len(loss_rpn_cls))])
xp.train.loss_rpn_reg.update(loss_rpn_reg, [j for j in range(len(loss_rpn_reg))])
xp.train.loss_bbox_cls.update(loss_bbox_cls, [j for j in range(len(loss_bbox_cls))])
xp.train.loss_bbox_reg.update(loss_bbox_reg, [j for j in range(len(loss_bbox_reg))])
xp.train.loss.update(loss, [j for j in range(len(loss))])
xp.train.learning_rate.update(learning_rate, [j for j in range(len(learning_rate))])


xp.valid.mAP.update(mAP,[j for j in range(len(mAP))])
xp.valid.mAR.update(mAR,[j for j in range(len(mAR))])
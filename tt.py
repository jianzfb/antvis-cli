# -*- coding: UTF-8 -*-
# @Time    : 2021/10/7 6:18 下午
# @File    : tt.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
import antvis.client.mlogger as mlogger
import numpy as np

project = 'face-det'
experiment = 'exp-5'
mlogger.config(token='ec7bf79ca31142df8ce14ee0e0a499a9')
print(mlogger.list())
mlogger.activate(project, experiment)

xp = mlogger.Container()
xp.train = mlogger.Container()
xp.train.accuracy = mlogger.metric.Average('accuracy')
print(xp.train.accuracy.get())

print(mlogger.tag.learning_rate.get())
#
# # 创建实验
# mlogger.config(project, experiment, token='ec7bf79ca31142df8ce14ee0e0a499a9')
#
# # 添加实验标签
# mlogger.tag.learning_rate = '0.01'
# mlogger.tag.batch_size = '126'
# mlogger.tag.optimizer = 'SGD'
# mlogger.tag.weight_decay = '0.0001'
#
# # xp = mlogger.Container()
# # xp.ss = mlogger.Container()
# # xp.ss.ff = mlogger.FileLogger('hello')
# # xp.ss.ff.update('/Users/jian/Downloads/iqiyi_1610978950796 (1).png')
#
# xp = mlogger.Container()
# xp.train = mlogger.Container()
# xp.train.accuracy = mlogger.metric.Average('accuracy')
#
# for j in range(10):
#   xp.train.accuracy.update(j)
#
# print(xp.train.accuracy.get())
#
# # xp = mlogger.Container()
# # xp.test = mlogger.Container()
# # xp.test.log = mlogger.complex.Text('output')
# #
# # # for j in range(10):
# # #   xp.test.log.update("{} run finish".format("preprocess"))
# #
# # print(xp.test.log.get())
# # print('s')
# # xp = mlogger.Container()
# # xp.train = mlogger.Container()
# # xp.train.parameter_distribution = mlogger.complex.Histogram('parameter dis')
# #
# # # for j in range(10):
# # #   data = np.random.randint(0, 10, (100, 40))
# # #   xp.train.parameter_distribution.update(data)
# #
# # print(xp.train.parameter_distribution.get())
# # print('s')
#
#
# # xp = mlogger.Container()
# # xp.text = mlogger.Container()
# # xp.text.mytable = mlogger.complex.Table('C')
# # # xp.text.mytable.r0c0 = 'a'
# # # xp.text.mytable.r0c1 = 'jin'
# # # xp.text.mytable.r1c0 = 'c'
# # # xp.text.mytable.r1c1 = 'd'
# # # xp.text.mytable.update()
# #
# # print(xp.text.mytable.get())
# # print('s')
#
#
# # xp = mlogger.Container()
# # xp.text = mlogger.Container()
# # xp.text.heat = mlogger.complex.Heatmap('D')
# # # mm = np.random.randint(0, 10, (10, 10))
# # # xp.text.heat.update(mm)
# #
# # print(xp.text.heat.get())
# # # print(mm)
# # print('s')
#
# # xp = mlogger.Container()
# # xp.test = mlogger.Container()
# # xp.test.img = mlogger.complex.Image('B')
# #
# # # for j in range(10):
# # #   xp.test.img.update(np.random.randint(0, 255, (100, 100)).astype(np.uint8))
# #
# # xp.test.img.get()
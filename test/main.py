# -*- coding: UTF-8 -*-
# @Time    : 2020-05-28 22:37
# @File    : app.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
import time
import numpy as np
import json
import antvis.client.mlogger as mlogger
# import tensorflow as tf
# import antvis.client.mlogger.tensorflow
# import io
# import matplotlib.pyplot as plt
# import os
# import re
# import torch

mlogger.config('127.0.0.1', 8999, token='42fb617800384df983edbd9509c2b2ba')
mlogger.activate('XX', 'exp.3')
xp = mlogger.Container()
xp.ff = mlogger.FileLogger('model file')
xp.ff.get()


# mlogger.config('127.0.0.1', 8999, 'XX', 'exp', token='42fb617800384df983edbd9509c2b2ba')
#
# # 上传1G文件
# xp = mlogger.Container()
# xp.ff = mlogger.FileLogger('model file')
# xp.ff.update('/Users/jian/Downloads/RR/pycharm-community-2020.2.1.dmg')
# mlogger.exit()



# # xp = mlogger.Container()
# # xp.tt = mlogger.tensorflow.Image('TT')
# # a = tf.random.normal((1, 100,100, 3))
# # b = tf.random.normal((1, 100,100, 3))
# # c = a*255 + b*255
# # c = tf.cast(c,tf.uint8)
# # d = xp.tt(c)
# #
# # with tf.Session() as sess:
# #     value = sess.run(d)
# #     print(value)
# #
# #
# # mlogger.update()
# # mlogger.exit()
#
# # # 1. 获得实验项目列表
# # print(mlogger.list())
# #
# # # 2. 激活实验
# # mlogger.activate('you', 'jian10')
# #
# # # 3. 创建实验
# # # mlogger.create_project('you', 'jian10')
# # # mlogger.activate('you', 'DD')
# #
# # 4. 添加可视化数据
# # 4.1 文本数据
# xp = mlogger.Container()
# xp.train = mlogger.Container()
# xp.train.log_1 = mlogger.complex.Text('T2')
# xp.train.log_2 = mlogger.complex.Text('T2')
#
# for _ in range(50):
#     xp.train.log_1.info('hello')
#     xp.train.log_2.warn('world')
# mlogger.update()
#
#
# # print(xp.train.log_1.get())
# # print(xp.train.log_2.get())
#
# xp.ss = mlogger.complex.Image("Save")
# xp.ss.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
# xp.ss.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
# xp.ss.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
# xp.ss.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
# xp.ss.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
# xp.ss.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
# xp.tt = mlogger.complex.Image("Save")
# xp.tt.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
# xp.tt.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
# xp.qq = mlogger.complex.Image("Save")
# xp.qq.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
# xp.qq.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
#
# xp.qq1 = mlogger.complex.Image("Save")
# xp.qq1.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
# xp.qq1.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
#
# xp.qq2 = mlogger.complex.Image("Save")
# xp.qq2.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
# xp.qq2.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
#
# xp.qq3 = mlogger.complex.Image("Save")
# xp.qq3.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
# xp.qq3.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
#
# xp.qq4 = mlogger.complex.Image("Save")
# xp.qq4.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
# xp.qq4.update(np.random.randint(0,255,[100,100,3], dtype=np.uint8))
#
#
# mlogger.update()
# # 4.2 时序数据
# xp.step = mlogger.metric.Simple('global step')
#
# for i in range(10):
#     xp.step.update(i)
# mlogger.update()
#
# # 4.3 散点图
# xp.pareto_front = mlogger.complex.Scatter('pareto front')
# xp.pareto_front.update([np.random.randint(0,10,[10]).tolist(),
#                         np.random.randint(0,10,[10]).tolist()])
#
# # 4.4 直方图
# xp.mm = mlogger.complex.Histogram('EE')
# xp.mm.update(np.random.random((10, 30)))
# mlogger.update()
# print('his')
# # print(xp.mm.get())
#
# # 4.5 柱状图
# xp.dis = mlogger.complex.Bar('DD')
# xp.dis.update(['x','y','z'],[10,100,9])
# mlogger.update()
#
# # 4.6 热力图
# xp.heat = mlogger.complex.Heatmap('H')
# xp.heat.update(np.random.randint(0,255,(500,500)))
# mlogger.update()
#
# # 4.7 表格数据
# xp.cc = mlogger.complex.Table("SO")
# xp.cc.r0c0 = 'A'
# xp.cc.r0c1 = 'B'
# xp.cc.r1c0 = 'c'
# xp.cc.r1c1 = 'D'
# xp.cc.update()
# mlogger.update()
# # print(xp.cc.get())
#
# # 4.8 标签
# mlogger.tag.learning_rate = '0.01'
# mlogger.tag.batch_size = '126'
# mlogger.tag.optimizer = 'SGD'
# mlogger.tag.weight_decay = '0.0001'
# mlogger.update()
# # mlogger.tag.cc.get()
#
# # # 4.9 文件
# # xp.ff = mlogger.FileLogger('model file')
# # xp.ff.update('/Users/jian/Downloads/TT/index.md')
# #
# # # 4.10 文件夹
# # xp.mm = mlogger.FolderLogger('fo')
# # xp.mm.update('/Users/jian/Downloads/TT/')
#
# # 4.11 环境监控
# xp.cpu = mlogger.CPU('train process')
# for _ in range(10):
#     xp.cpu.update()
# mlogger.update()
# # print(xp.cpu.get())
#
# xp.mem = mlogger.Memory('train process-mem')
# for _ in range(10):
#     xp.mem.update()
# mlogger.update()
#
# # 4.12 git环境监控
# mlogger.exit()
# #
# # # # 获得记录数据
# # # print(xp.train.log_1.get())
# # # print(xp.train.log_2.get())
# #
# # # 4.2 时序数据
# # xp.step = mlogger.metric.Simple('global step')
# #
# # for i in range(10):
# #     xp.step.update(i)
# # mlogger.update()
# # # print('xp step')
# # # print(xp.step.get())
# #
# # # 4.3 散点图
# # xp.pareto_front = mlogger.complex.Scatter('pareto front')
# # xp.pareto_front.update([np.random.randint(0,10,[10]).tolist(),
# #                         np.random.randint(0,10,[10]).tolist()])
# # mlogger.update()
# # # print('xp pareto front')
# # # print(xp.pareto_front.get())
# #
# # # 4.4 直方图
# # xp.mm = mlogger.complex.Histogram('EE')
# # xp.mm.update(np.random.random((10, 30)))
# # mlogger.update()
# # # print('histgram')
# # # print(xp.mm.get())
# #
# # # 4.5 柱状图
# # xp.dis = mlogger.complex.Bar('DD')
# # xp.dis.update(['x','y','z'],[10,100,9])
# # mlogger.update()
# # # print('bar')
# # # print(xp.dis.get())
# #
# # # 4.6 热力图
# # xp.heat = mlogger.complex.Heatmap('H')
# # xp.heat.update(np.random.randint(0,255,(500,500)))
# # mlogger.update()
# # # print('heat')
# # # print(xp.heat.get())
# #
# # # 4.7 表格数据
# # xp.cc = mlogger.complex.Table("SO")
# # xp.cc.r0c0 = 'A'
# # xp.cc.r0c1 = 'B'
# # xp.cc.r1c0 = 'c'
# # xp.cc.r1c1 = 'D'
# # xp.cc.update()
# # mlogger.update()
# # # print(xp.cc.get())
# # # 5 文件日志
# # xp.hh = mlogger.FileLogger('xxx')
# # xp.hh.update('/Users/zhangjian52/Downloads/train - 2020-08-12T151311.250.log')
# #
# #
# # # 6 标签
# # # mlogger.tag.A = 'A'
# # mlogger.tag.B.C.D = 'bcn'
# # mlogger.update()
# # print(mlogger.tag.B.C.D.get())

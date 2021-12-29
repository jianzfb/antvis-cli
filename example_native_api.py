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
experiment = 'my_exp_4'

# 创建实验
mlogger.config(project, experiment, token='d7030d4a2bc646c29c40bc3b425d1e3f', server="BASELINE")

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

# xp.test = mlogger.Container()
# xp.test.show1 = mlogger.complex.Image("S")
# xp.test.show2 = mlogger.complex.Image("S")
# xp.test.show3 = mlogger.complex.Image("S")
# xp.test.show4 = mlogger.complex.Image("S")
#
# xp.pareto_front_1 = mlogger.complex.Scatter(plot_title='pareto front 1', is_series=False)
# xp.pareto_front_1.update(np.random.randint(0,10,(2,10)))
# xp.pareto_front_2 = mlogger.complex.Scatter(plot_title='pareto front 2', is_series=False)
# xp.pareto_front_2.update(np.random.randint(0,10,[10]).tolist(), np.random.randint(0,10,[10]).tolist())
# xp.pareto_front_3 = mlogger.complex.Scatter(plot_title='pareto front 3', is_series=True)
# for index in range(10):
#   xp.pareto_front_3.update(np.random.randint(0,20))
#
# xp.dis = mlogger.complex.Bar('bar')
# # 使用update函数，记录数据
# xp.dis.update(['x','y','z'],['a','b','c'])
#
# # 添加容器的热力图数据记录器
# xp.heat = mlogger.complex.Heatmap('H')
# # 使用update函数，记录数据。自动将输入的数据归一化。
# xp.heat.update(np.random.randint(0,255,(500,500)))
#
# # 添加容器的折线数据记录器(非序列化模式，每次update更新数据都会覆盖之前的数据)
# xp.curve_1 = mlogger.complex.Line(plot_title='curve 1', is_series=False)
# # 使用update函数，记录数据
# xp.curve_1.update(np.random.randint(0,10,(2,10)))
# xp.curve_2 = mlogger.complex.Line(plot_title='curve 2', is_series=False)
# xp.curve_2.update(np.random.randint(0,10,[10]).tolist(), np.random.randint(0,10,[10]).tolist())
#
# # 添加容器的散点数据记录器(序列化模式，每次update更新数据将递增)
# xp.curve_3 = mlogger.complex.Line(plot_title='curve 3', is_series=True)
# for index in range(10):
#   xp.curve_3.update(np.random.randint(0,20))
#
# for index in range(10):
#   data = np.random.random((255,255, 3))
#   xp.test.show1.update(data)
#   data = np.random.random((255,255, 3))
#   xp.test.show2.update(data)
#   data = np.random.random((255,255, 3))
#   xp.test.show3.update(data)
#   data = np.random.random((255,255, 3))
#   xp.test.show4.update(data)
#   mlogger.update()
#
#   time.sleep(10)


# mlogger.config(token='706cb1895fb84507b6fa4703bfbe3026')
# # 获得指定项目下的实验列表
# experiment_list = mlogger.list(project='Hello')
#
# print(experiment_list)

v = mlogger.Variable()
v.b = mlogger.FloatVar(1.0)

v.b.set(10.0)
print(v.b.get())
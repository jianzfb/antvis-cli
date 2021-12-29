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
import antvis.client.mlogger as mlogger

project = 'AA'
experiment = 'my_exp_4'

# 创建实验
mlogger.config(project, experiment, token='e4d8e05850a04280a55aa012d7f68eba')

v = mlogger.Variable()
# 测试浮点值
v.b = mlogger.FloatVar(1.0)
v.b.set(10.0)
print(v.b.get())

# 测试整数值
v.c = mlogger.IntVar(1)
v.c.set(20)
print(v.c.get())

# 测试bool值
v.d = mlogger.IntVar(False)
v.d.set(True)
print(v.d.get())

# 测试字符串
v.e = mlogger.StringVar("hello")
v.e.set("world")
print(v.e.get())

# # 测试trigger
# v.m = mlogger.TriggerVar()
# v.m.waitting()
# print("hello")

xp = mlogger.Container()
xp.test = mlogger.Container()
xp.pareto_front_1 = mlogger.complex.Scatter(plot_title='pareto front 1', is_series=False)
xp.pareto_front_1.update(np.random.randint(0,10,(2,10)))

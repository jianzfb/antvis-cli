# -*- coding: UTF-8 -*-
# @Time    : 2021/10/7 6:18 下午
# @File    : example_native_api.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from antvis.client.style.visdom import Visdom
import numpy as np

vis = Visdom('QQ', '706cb1895fb84507b6fa4703bfbe3026')

for index in range(10):
  vis.scatter(index, index, 'HELLO', update=True)

vis.scatter([3,4,1,2,4],[4,3,1,2,4],'WANGWANG', update=False)
vis.scatter(np.random.random((2,10)), None, 'QQ', update=False)
vis.scatter(np.random.random((2,4)), None, 'WW', update=False)

for index in range(10):
  vis.line(index, index, 'LA', update=True)

vis.line([3,4,1,2,4],[4,3,1,2,4],'LB', update=False)
vis.line(np.random.random((2,10)), None, 'LC', update=False)
vis.line(np.random.random((2,4)), None, 'LD', update=False)


vis.image(np.random.randint(0, 255, (3, 255, 255)).astype(np.uint8), win='UUII')
kv_dict = {'A': 'NI', 'B': 'HAO'}
vis.tags(kv_dict, 'PARAM')

for index in range(10):
  vis.text('hello %d'%index, 'SHOU')

print('hello')
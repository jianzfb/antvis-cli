# -*- coding: UTF-8 -*-
# @Time    : 2021/10/7 6:18 下午
# @File    : example_native_api.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
import numpy as np
import torch
import time
from antvis.client.style.tensorboard import SummaryWriter
writer = SummaryWriter('TYZ-ui9900', '706cb1895fb84507b6fa4703bfbe3026')

# # 测试scalar
# for index in range(100):
#   writer.add_scalar('A', index)
#
# 测试scalars
for index in range(100):
  writer.add_scalars('VAL', {'A': index, 'B': index*3, 'C': index*4, 'D': index*5})
  time.sleep(10)
  # writer.flush()


# # 测试image
# data = np.random.random((255,255))
# data = torch.from_numpy(data)
# writer.add_image('SHOW', data, dataformats='HW')
#
# data = np.random.random((3, 255,255))
# data = torch.from_numpy(data)
# writer.add_image('SHOW_A', data, dataformats='CHW')
#
# data = np.random.random((255,255, 3))
# data = torch.from_numpy(data)
# writer.add_image('SHOW_B', data, dataformats='HWC')
#
# # 测试histogram
# data = np.random.random((355,255))
# writer.add_histogram('HIS', data, max_bins=1000)

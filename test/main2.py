from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

import antvis.client.mlogger as mlogger
import numpy as np
import time


if __name__ == "__main__":
  # 1.step 配置日志环境
  mlogger.config('127.0.0.1',
                 8999,
                 'det',
                 'b',
                 token='3bdbf5aa1c274b05971bdf2b58508816')

  # 2.step 设置实验标签
  mlogger.tag.learning_rate = '0.01'
  mlogger.tag.batch_size = '126'
  mlogger.tag.optimizer = 'SGD'
  mlogger.tag.weight_decay = '0.0001'

  # 2.step 配置容器
  container_1 = mlogger.Container()
  container_2 = mlogger.Container()

  # 2.1.step 配置绘制图表——Simple
  container_1.growth_curve = mlogger.metric.Simple('growth')

  for _ in range(50):
    container_1.growth_curve.update(_)
  mlogger.update()

  # 2.2.step 配置绘制图表——Image
  container_1.image_show_1 = mlogger.complex.Image('image-1')
  container_1.image_show_2 = mlogger.complex.Image('image-2')

  # 2.3.step 配置绘制图表——Histogram
  container_1.check_his = mlogger.complex.Histogram('check-his', BINS=200)

  for _ in range(5):
    container_1.image_show_1.update(np.random.randint(0, 255, (255, 255, 3)))
    container_1.image_show_2.update(np.random.random((512, 256, 3)))
    container_1.check_his.update(np.random.random((50, 50)))
  mlogger.update()

  # 2.4.step 配置绘制图表——Bar
  container_1.check_bar_1 = mlogger.complex.Bar('check-bar-1')
  container_1.check_bar_1.update([5,6,7,8], [10,40,100,1])

  container_1.check_bar_2 = mlogger.complex.Bar('check-bar-2')
  container_1.check_bar_2.update(['a','b','c','d'], [1,2,3,4])
  mlogger.update()

  # 2.5.step 配置绘制图表——Heatmap
  container_2.check_heatmap = mlogger.complex.Heatmap('check-heatmap')
  container_2.check_heatmap.update(np.random.randint(0, 255, (500, 500)))
  mlogger.update()
  print('sdf')

  # 2.6.step 配置绘制图表——Text
  container_2.check_text = mlogger.complex.Text('check-text')

  # 2.7.step 配置绘制图表——Table
  container_2.check_table = mlogger.complex.Table('check-table')

  # 2.8.step 配置绘制图表——Scatter
  container_2.check_scatter = mlogger.complex.Scatter('check-scatter')

  # 2.9.step 监控
  container_2.cpu = mlogger.CPU('train process')
  container_2.mem = mlogger.Memory('train process-mem')

  for _ in range(10):
    container_2.check_heatmap.update(np.random.randint(0, 255, (500, 500)))
    container_2.check_text.update('hello %d'%_)
    container_2.check_table.r0c0 = 'A'
    container_2.check_table.r2c2 = 'C'
    container_2.check_table.update()

    container_2.check_scatter.update([np.random.randint(0, 10, [10]).tolist(),
                            np.random.randint(0, 10, [10]).tolist()])

    container_2.cpu.update()
    container_2.mem.update()
    time.sleep(1)
    mlogger.update()

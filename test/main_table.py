from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
import time
import numpy as np
import json
import sys
sys.path.insert(0, '/workspace/project/antvis-cli')
import antvis.client.mlogger as mlogger

project = 'AA'
experiment = 'solidball-sport-udm8'

# 创建实验
token = '247ac6502f714dc4a3c415fa3af00023'
mlogger.config(project, experiment, token=token, auto_suffix=False, server="BASELINE")
xp = mlogger.Container()

xp.cc = mlogger.complex.Table("CDF")
xp.cc.r0c0 = 'ets'
xp.cc.r1c0 = '1223'
xp.cc.update()
mlogger.update()


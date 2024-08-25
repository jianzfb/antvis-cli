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
experiment = 'my_exp_4'

token = '247ac6502f714dc4a3c415fa3af00023'
mlogger.config(project, experiment, token=token)
xp = mlogger.Container()

xp.ff = mlogger.FileLogger('model file')
xp.ff.update('/workspace/gg.py')
print("hl")
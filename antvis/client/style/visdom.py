# -*- coding: UTF-8 -*-
# @Time    : 2021/10/29 2:09 下午
# @File    : visdom.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
import antvis.client.mlogger as mlogger
import numpy as np
import os
import logging


class Visdom(object):
  def __init__(self, env='', token=''):
    assert(token != '')
    assert(env != '')
    mlogger.config(env, env, token=token)
    self.container = mlogger.Container()

  def line(self, Y, X=None, win=None, env=None, opts=None, update=None, name=None):
    # 支持list,标量
    assert(win is not None)
    if not getattr(self.container, win):
      if name is None:
        name = win
      if update:
        setattr(self.container, win, mlogger.complex.Line(name, is_series=True))
      else:
        setattr(self.container, win, mlogger.complex.Line(name, is_series=False))

    getattr(self.container, win).update(Y, X)

  def scatter(self,Y, X=None, win=None, env=None, opts=None, update=None, name=None):
    # 支持list, 标量
    assert(win is not None)
    if not getattr(self.container, win):
      if name is None:
        name = win
      if update:
        setattr(self.container, win, mlogger.complex.Scatter(name, is_series=True))
      else:
        setattr(self.container, win, mlogger.complex.Scatter(name, is_series=False))

    getattr(self.container, win).update(Y, X)

  def image(self, img, win=None, env=None, opts=None):
    """
    This function draws an img. It takes as input an 'CxHxW' or 'HxW' tensor img that
    contains the image. The array values can be float in [0,1] or uint8 in [0,255]

    增强对img格式的支持
    支持 HxWxC
    """
    assert(win is not None)
    nchannels = img.shape[0] if img.ndim == 3 else 1
    if nchannels == 1:
      img = np.squeeze(img)
      img = img[np.newaxis, :, :].repeat(3, axis=0)

    if 'float' in str(img.dtype):
      if img.max() <= 1:
        img = img * 255
      img = np.uint8(img)
    assert('uint8' in str(img.dtype))

    if img.shape[2] != 3:
      # CxHxW格式
      img = np.transpose(img, (1, 2, 0))

    if not getattr(self.container, win):
      setattr(self.container, win, mlogger.complex.Image(win))

    getattr(self.container, win).update(img)

  def tags(self, kv_dict, win=None, env=None, opts=None, append=False):
    assert(win is not None)
    if not getattr(self.container, win):
      setattr(self.container, win, mlogger.complex.Table(win))
    count = 0
    for k,v in kv_dict.items():
      setattr(getattr(self.container, win), 'r%dc%d'%(count, 0), str(k))
      setattr(getattr(self.container, win), 'r%dc%d'%(count, 1), str(v))

      count += 1

    getattr(self.container, win).update()

  def text(self, s, win=None, env=None, opts=None, append=False):
    assert(win is not None)
    if not getattr(self.container, win):
      setattr(self.container, win, mlogger.complex.Text(win))

    # 与visdom功能存在差异，不会对html代码进行格式渲染，仅作为字符串处理
    logging.warning('Have different feature with VISDOM, dont support html render.')
    getattr(self.container, win).update(s)

  def svg(self, svgstr=None, svgfile=None, win=None, env=None, opts=None):
    assert(win is not None)
    if not getattr(self.container, win):
      setattr(self.container, win, mlogger.complex.Svg(win))

    assert(svgstr is not None or svgfile is not None)

    if svgstr is not None:
      getattr(self.container, win).update(svgstr)
    else:
      if not os.path.exists(svgfile):
        logging.error('%s dont exist'%svgfile)
        return

      with open(svgfile, 'r') as fp:
        getattr(self.container, win).update(fp.read())
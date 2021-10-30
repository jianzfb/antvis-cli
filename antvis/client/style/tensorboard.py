# -*- coding: UTF-8 -*-
# @Time    : 2021/10/29 8:27 下午
# @File    : tensorboard.py
# @Author  : jian<jian@mltalker.com>
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
import antvis.client.mlogger as mlogger
import numpy as np
import os
import logging
import torch


class SummaryWriter(object):
  def __init__(self, name='', token=''):
    assert(token != '')
    assert(name != '')
    mlogger.config(name, name, token=token)
    self.container = mlogger.Container()

  def add_histogram(self, tag, values, global_step=None, max_bins=None):
    """
    tag (string): Data identifier
    values (torch.Tensor, numpy.array): Values to build histogram
    global_step (int): Global step value to record

    """
    if not getattr(self.container, tag):
      max_bins = 100 if max_bins is None else max_bins
      setattr(self.container, tag, mlogger.complex.Histogram(tag, BINS=max_bins))

    if type(values) == torch.Tensor:
      values = values.detach().cpu().numpy()

    if type(values) != np.ndarray:
      logging.error('Only support torch.Tensor, numpy.array')
      return

    getattr(self.container, tag).update(values, global_step)

  def add_scalar(self, tag, scalar_value, global_step=None):
    scalar_value = (float)(scalar_value)
    if not getattr(self.container, tag):
      setattr(self.container, tag, mlogger.complex.Line(tag, is_series=True))

    getattr(self.container, tag).update(scalar_value, global_step)

  def add_scalars(self, main_tag, tag_scalar_dict, global_step=None):
    for k, v in tag_scalar_dict.items():
      tag = '%s_%s'%(main_tag, k)
      if not getattr(self.container, tag):
        setattr(self.container, tag, mlogger.complex.Line(main_tag, is_series=True))

    for k, v in tag_scalar_dict.items():
      v = (float)(v)
      tag = '%s_%s' % (main_tag, k)
      getattr(self.container, tag).update(v, global_step)

  def add_image(self, tag, img_tensor, global_step=None, dataformats='CHW'):
    """
    tag (string): Data identifier
    img_tensor (torch.Tensor, numpy.array): Image data
    global_step (int): Global step value to record

    """
    assert (dataformats in ['CHW', 'HWC', 'HW'])
    if type(img_tensor) == torch.Tensor:
      img_tensor = img_tensor.detach().cpu().numpy()

    if type(img_tensor) != np.ndarray:
      logging.error('Only support torch.Tensor, numpy.array')
      return

    if dataformats == 'HW':
      assert(img_tensor.ndim == 2)

    nchannels = img_tensor.shape[0] if img_tensor.ndim == 3 else 1
    if nchannels == 1:
      img_tensor = np.squeeze(img_tensor)
      img_tensor = img_tensor[np.newaxis, :, :].repeat(3, axis=0)
      dataformats = 'CHW'

    if dataformats == 'CHW':
      assert(img_tensor.shape[0] == 3)
    if dataformats == 'HWC':
      assert (img_tensor.shape[2] == 3)

    if 'float' in str(img_tensor.dtype):
      if img_tensor.max() <= 1:
        img_tensor = img_tensor * 255
      img_tensor = np.uint8(img_tensor)
    assert('uint8' in str(img_tensor.dtype))

    if dataformats == "CHW":
      # to HWC
      img_tensor = np.transpose(img_tensor, (1, 2, 0))

    if not getattr(self.container, tag):
      setattr(self.container, tag, mlogger.complex.Image(tag))

    getattr(self.container, tag).update(img_tensor)

  def add_graph(self, model, input_to_model=None):
    raise NotImplementedError

  def flush(self):
    mlogger.update()
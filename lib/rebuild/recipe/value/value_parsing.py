#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

class value_parsing(object):

  MASK_DELIMITER = ':'

  _mav = namedtuple('_mav', 'mask, value')
  @classmethod
  def split_mask_and_value(clazz, s):
    mask, delimiter, value = s.partition(clazz.MASK_DELIMITER)
    if delimiter != clazz.MASK_DELIMITER:
      raise ValueError('no valid mask delimiter found: %s' % (s))
    return clazz._mav(mask.strip(), value.strip())

  @classmethod
  def strip_mask(clazz, s):
    _, value = clazz.split_mask_and_value(s)
    return value
  

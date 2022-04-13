#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from .value_error import value_error

class value_parsing(object):

  MASK_DELIMITER = ':'

  _parsed_value = namedtuple('_parsed_value', 'mask, value')

  _mav = namedtuple('_mav', 'mask, value')
  @classmethod
  def split_mask_and_value(clazz, origin, s):
    mask, delimiter, value = s.partition(clazz.MASK_DELIMITER)
    if delimiter != clazz.MASK_DELIMITER:
      value_error.raise_error(origin, 'no valid mask delimiter found: %s' % (s))
    return clazz._mav(mask.strip(), value.strip())

  @classmethod
  def strip_mask(clazz, origin, s):
    _, value = clazz.split_mask_and_value(origin, s)
    return value

  @classmethod
  def parse_key_value(clazz, origin, text):
    check.check_value_origin(origin)
    check.check_string(text)
    key, delimiter, value = text.partition(':')
    key = key.strip()
    if not key:
      raise value_error.raise_error(origin, '%s: invalid step value key: \"%s\"' % (origin, text))
    if not delimiter:
      return clazz._parsed_value(None, None)
    value_text = value.strip() or None
    return clazz._parsed_value(None, value_text)

  @classmethod
  def parse_mask_and_value(clazz, origin, text):
    check.check_value_origin(origin)
    check.check_string(text)
    mask, value = clazz.split_mask_and_value(origin, text)
    return clazz._parsed_value(mask, value)

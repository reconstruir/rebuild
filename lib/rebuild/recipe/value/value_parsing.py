#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common import check

class value_parsing_error(Exception):
  def __init__(self, message, filename, line_number):
    super(value_parsing_error, self).__init__()
    self.message = message
    self.filename = filename
    self.line_number = line_number

  def __str__(self):
    if not self.line_number:
      return '%s: %s' % (self.filename, self.message)
    else:
      return '%s:%s: %s' % (self.filename, self.line_number, self.message)

class value_parsing(object):

  MASK_DELIMITER = ':'

  parsed_value = namedtuple('parsed_value', 'mask, value')

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

  @classmethod
  def parse_key_value(clazz, origin, text):
    check.check_value_origin(origin)
    check.check_string(text)
    key, delimiter, value = text.partition(':')
    key = key.strip()
    if not key:
      raise clazz.raise_error(origin, '%s: invalid step value key: \"%s\"' % (origin, text))
    if not delimiter:
      return clazz.parsed_value(None, None)
    value_text = value.strip() or None
    return clazz.parsed_value(None, value_text)

  @classmethod
  def parse_mask_and_value(clazz, origin, text):
    check.check_value_origin(origin)
    check.check_string(text)
    mask, value = clazz.split_mask_and_value(text)
    return clazz.parsed_value(mask, value)
  
  @classmethod
  def raise_error(clazz, origin, msg, starting_line_number = None):
    starting_line_number = starting_line_number or 0
    check.check_value_origin(origin)
    check.check_string(msg)
    raise value_parsing_error(msg, origin.filename, origin.line_number + starting_line_number)

  

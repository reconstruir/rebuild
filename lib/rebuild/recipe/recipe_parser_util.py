#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from bes.key_value import key_value
from bes.text import comments

from .value import value_factory

class recipe_parser_util(object):

  MASK_DELIMITER = ':'

  @classmethod
  def split_mask_and_value(clazz, s):
    mask, delimiter, value = s.partition(clazz.MASK_DELIMITER)
    if delimiter != clazz.MASK_DELIMITER:
      raise ValueError('no valid mask delimiter found: %s' % (s))
    return ( mask.strip(), value.strip() )
  
  @classmethod
  def strip_mask(clazz, s):
    _, value = clazz.split_mask_and_value(s)
    return value

  @classmethod
  def parse_key(clazz, origin, text):
    'Parse only the key'
    check.check_string(text)
    key, _, _ = comments.strip_line(text).partition(':')
    return key.strip()

  @classmethod
  def make_key_value(clazz, origin, text, node, value_class_name):
    check.check_value_origin(origin)
    check.check_string(text)
    check.check_node(node)
    check.check_string(value_class_name)
    text = comments.strip_line(text)
    key, delimiter, value = text.partition(':')
    key = key.strip()
    if not key:
      raise ValueError('%s: invalid step value key: \"%s\"' % (origin, text))
    if not delimiter:
      return key_value(key, None)
    value_text = value.strip() or None
    if not value_text:
      return key_value(key, None)
    value = value_factory.create_with_class_name(origin, value_text, node, value_class_name)
    return key_value(key, value)

  @classmethod
  def make_value(clazz, origin, text, node, value_class_name):
    if origin:
      check.check_value_origin(origin)
    check.check_node(node)
    check.check_string(value_class_name)
    return value_factory.create_with_class_name(origin, text, node, value_class_name)

  @classmethod
  def value_default(clazz, class_name):
    value_class = value_factory.get_class(class_name)
    return value_class.default_value(class_name)

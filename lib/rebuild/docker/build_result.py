#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from collections import namedtuple
from bes.common.check import check
from bes.common.node import node
from bes.key_value.key_value_list import key_value_list
from bes.text.string_list import string_list

class build_result(object):

  _parse_build_result = namedtuple('_parse_build_result', 'image_id, tag')
  @classmethod
  def parse_build_result(clazz, text):
    'Parse the docker build result text and return the interesting info about it.'
    image_id = clazz._extract_image_id(text)
    tag = clazz._extract_tag(text)
    return clazz._parse_build_result(image_id, tag)

  @classmethod
  def _extract_image_id(clazz, text):
    f = re.findall('Successfully\sbuilt\s([0-9a-fA-F]+)', text)
    if f and len(f) == 1:
      return f[0]
    return None
  
  @classmethod
  def _extract_tag(clazz, text):
    f = re.findall('Successfully\stagged\s(.*)', text)
    if f and len(f) == 1:
      return f[0]
    return None

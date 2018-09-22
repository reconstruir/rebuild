#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

class source_item(namedtuple('source_item', 'filename, checksum')):
  
  def __new__(clazz, filename, checksum):
    return clazz.__bases__[0].__new__(clazz, filename, checksum)

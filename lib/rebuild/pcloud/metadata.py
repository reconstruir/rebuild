#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common import check

class metadata(namedtuple('metadata', 'name, size, category, content_type, hash, contents')):

  CATEGORIES = {
    0: 'uncategorized',
    1: 'image',
    2: 'video',
    3: 'audio',
    4: 'document',
    5: 'archive',
  }

  def __new__(clazz, name, size, category, content_type, hash, contents):
    return clazz.__bases__[0].__new__(clazz, name, size, category, content_type, hash, contents)

check.register_class(metadata)

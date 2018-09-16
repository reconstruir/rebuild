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

  CATEGORY_IDS = sorted(CATEGORIES.keys())
  CATEGORY_NAMES = sorted(CATEGORIES.values())
  
  def __new__(clazz, name, size, category, content_type, hash, contents):
    return clazz.__bases__[0].__new__(clazz,
                                      name,
                                      size,
                                      clazz.parse_category(category),
                                      content_type,
                                      hash,
                                      contents)
  @classmethod
  def parse_category(clazz, category):
    if check.is_int(category):
      if category in clazz.CATEGORIES:
        return clazz.CATEGORIES[category]
    elif check.is_string(category):
      if category.lower() in clazz.CATEGORY_NAMES:
        return category.lower()
    raise ValueError('Invalid category: %s' % (str(category)))

check.register_class(metadata)

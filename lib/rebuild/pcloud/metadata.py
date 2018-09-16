#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common import check

class metadata(namedtuple('metadata', 'name, is_folder, size, category, content_type, content_hash, contents')):
  '''
  Class representation for pcloud metadata
  https://docs.pcloud.com/structures/metadata.html
  '''

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
  
  def __new__(clazz, name, is_folder, size, category, content_type, content_hash, contents):
    if not is_folder:
      category = clazz.parse_category(category)
    else:
      if category is not None:
        raise ValueError('Invalid category for folder: %s' % (str(category)))
      
    return clazz.__bases__[0].__new__(clazz,
                                      name,
                                      is_folder,
                                      size,
                                      category,
                                      content_type,
                                      content_hash,
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

  @classmethod
  def parse_dict(clazz, d):
    check.check_dict(d)
    name = d['name']
    is_folder = d['isfolder']
    if is_folder:
      size = None
      category = None
      content_type = None
      content_hash = None
      contents = [ clazz.parse_dict(d) for d in d['contents'] ]
    else:
      size = d['size']
      category = d['category']
      content_type = d['contenttype']
      content_hash = d['hash']
      contents = None
    return clazz(name, is_folder, size, category, content_type, content_hash, contents)
  
check.register_class(metadata)

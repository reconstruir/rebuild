#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import check

class metadata(namedtuple('metadata', 'name, pcloud_id, is_folder, size, category, content_type, content_hash, contents, checksum')):
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
  
  def __new__(clazz, name, pcloud_id, is_folder, size, category, content_type,
              content_hash, contents, checksum):
    if is_folder:
      if category is not None:
        raise ValueError('Invalid category for folder: %s' % (str(category)))
      if checksum:
        raise ValueError('Invalid checksum for folder: %s' % (str(category)))
    else:
      category = clazz.parse_category(category)
    return clazz.__bases__[0].__new__(clazz,
                                      name,
                                      pcloud_id,
                                      is_folder,
                                      size,
                                      category,
                                      content_type,
                                      content_hash,
                                      contents,
                                      checksum)
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
    is_folder = bool(d['isfolder'])
    if is_folder:
      size = None
      category = None
      content_type = None
      content_hash = None
      if 'contents' in d:
        contents = [ clazz.parse_dict(item) for item in d['contents'] ]
      else:
        contents = None
      assert 'folderid' in d
      pcloud_id = d['folderid']
    else:
      size = d['size']
      category = d['category']
      content_type = d['contenttype']
      content_hash = d['hash']
      contents = None
      assert 'fileid' in d
      pcloud_id = d['fileid']
    return clazz(name, pcloud_id, is_folder, size, category, content_type,
                 content_hash, contents, None)
  
  def mutate_checksum(self, checksum):
    return self.__class__(self.name, self.pcloud_id, self.is_folder, self.size, self.category,
                          self.content_type, self.content_hash, self.contents,
                          checksum)
  
  def mutate_contents(self, contents):
    return self.__class__(self.name, self.pcloud_id, self.is_folder, self.size, self.category,
                          self.content_type, self.content_hash, contents,
                          self.checksum)
  
check.register_class(metadata)

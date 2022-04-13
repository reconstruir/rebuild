#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple
from bes.system.check import check
from bes.text.string_list import string_list

class pcloud_metadata(namedtuple('pcloud_metadata', 'name, path, pcloud_id, is_folder, size, category, content_type, content_hash, contents, checksum, created, modified')):
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
  
  def __new__(clazz, name, d_path, pcloud_id, is_folder, size, category, content_type,
              content_hash, contents, checksum, created, modified):
    if is_folder:
      if category is not None:
        raise ValueError('Invalid category for folder: %s' % (str(category)))
      if checksum:
        raise ValueError('Invalid checksum for folder: %s' % (str(category)))
    else:
      category = clazz.parse_category(category)
    return clazz.__bases__[0].__new__(clazz,
                                      name,
                                      d_path,
                                      pcloud_id,
                                      is_folder,
                                      size,
                                      category,
                                      content_type,
                                      content_hash,
                                      contents,
                                      checksum,
                                      created,
                                      modified)
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
    return clazz._parse_dict_with_folder(d, None)

  @classmethod
  def _parse_dict_with_folder(clazz, d, folder):
    check.check_dict(d)
    name = d['name']
    if folder:
      d_path = path.join(folder, name)
    else:
      d_path = name
    is_folder = bool(d['isfolder'])
    created = d['created']
    modified = d['modified']
    if is_folder:
      size = None
      category = None
      content_type = None
      content_hash = None
      if 'contents' in d:
        contents = [ clazz._parse_dict_with_folder(item, d_path) for item in d['contents'] ]
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
    return pcloud_metadata(name, d_path,  pcloud_id, is_folder, size, category, content_type,
                           content_hash, contents, None, created, modified)
  
  def mutate_checksum(self, checksum):
    return self.__class__(self.name, self.path, self.pcloud_id, self.is_folder, self.size, self.category,
                          self.content_type, self.content_hash, self.contents,
                          checksum, self.created, self.modified)
  
  def mutate_contents(self, contents):
    return self.__class__(self.name, self.path, self.pcloud_id, self.is_folder, self.size, self.category,
                          self.content_type, self.content_hash, contents,
                          self.checksum, self.created, self.modified)
  def list_files(self, recursive = False):
    result = string_list()
    self._collect_files(self, result)
    result.sort()
    return result

  @classmethod
  def _collect_files(clazz, md, result):
    if md.is_folder:
      for child in md.contents or []:
        clazz._collect_files(child, result)
    else:
      result.append(md.path)
    
check.register_class(pcloud_metadata)

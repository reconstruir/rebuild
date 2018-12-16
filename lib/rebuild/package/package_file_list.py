#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path, hashlib
from collections import namedtuple
from bes.common import check, json_util, object_util, type_checked_list
from bes.compat import StringIO
from bes.fs import file_util

from .package_file import package_file
  
class package_file_list(type_checked_list):

  __value_type__ = package_file
  
  def __init__(self, values = None):
    super(package_file_list, self).__init__(values = values)

  @classmethod
  def cast_value(clazz, entry):
    if isinstance(entry, ( tuple, list )):
      return package_file(*entry)
    return entry
    
  def to_json(self):
    return json_util.to_json(self._values, indent = 2)
    
  def to_simple_list(self):
    return [ x.to_list() for x in self ]
    
  @classmethod
  def from_json(clazz, text):
    o = json.loads(text)
    check.check_list(o)
    return clazz.from_simple_list(o)
    
  @classmethod
  def from_simple_list(clazz, l):
    check.check_list(l)
    result = clazz()
    for item in l:
      check.check_list(item)
      assert len(item) == 3
      check.check_string(item[0])
      check.check_string(item[1])
      check.check_bool(item[2])
      result.append(package_file(item[0], item[1], item[2]))
    return result
    
  @classmethod
  def from_files(clazz, filenames, files_with_hardcoded_paths, root_dir = None, function_name = None):
    filenames = object_util.listify(filenames)
    files_with_hardcoded_paths = files_with_hardcoded_paths or set()
    result = clazz()
    for filename in filenames:
      has_hardcoded_path = filename in files_with_hardcoded_paths
      result.append(package_file.from_file(filename, has_hardcoded_path, root_dir = root_dir, function_name = function_name))
    return result

  def save_checksums_file(self, filename):
    file_util.save(filename, content = self.to_json(), codec = 'utf8')

  @classmethod
  def load_checksums_file(clazz, filename):
    try:
      content = file_util.read(filename)
    except IOError as ex:
      return None
    return clazz.from_json(content)
  
  def filenames(self):
    return [ c.filename for c in self ]

  def reload(self, root_dir = None, function_name = None):
    new_values = []
    for value in self:
      new_values.append(package_file.from_file(value.filename, False, root_dir = root_dir, function_name = function_name))
    self._values = new_values
  
  def verify(self, root_dir = None):
    current = self[:]
    current.reload(root_dir = root_dir)
    return self == current

  def has_filename(self, filename):
    current = self[:]
    current.reload(root_dir = root_dir)
    return self == current

  def has_filename(self, filename):
    current = self[:]
    current.reload(root_dir = root_dir)
    return self == current

  def checksum(self):
    'Return a checksum of the files and file checksums themselves.'
    buf = StringIO()
    for value in self:
      buf.write(str(value))
    return hashlib.sha256(buf.getvalue().encode('utf-8')).hexdigest()

  def to_dict(self):
    'Return a dictionary of filenames to checksums.'
    result = {}
    for value in self:
      result[value.filename] = value.checksum
    return result

check.register_class(package_file_list, include_seq = False)

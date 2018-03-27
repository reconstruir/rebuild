#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from bes.common import object_util
from rebuild.base import package_descriptor

class package_db_entry(object):

  def __init__(self, descriptor, files):
    assert isinstance(descriptor, package_descriptor)
    assert isinstance(files, list)
    self.descriptor = descriptor
    self.files = files

  def __str__(self):
    return '%s[%s]' % (str(self.descriptor), ', '.join(self.files))

  def __eq__(self, other):
    if not other:
      return False
    return self.__dict__ == other.__dict__

  def to_dict(self):
    return {
      'descriptor': self.descriptor.to_dict(),
      'files': self.files,
    }

  @classmethod
  def parse_dict(clazz, d):
    assert 'descriptor' in d
    assert 'files' in d
    descriptor = d['descriptor']
    assert isinstance(descriptor, dict)
    descriptor = package_descriptor.parse_dict(descriptor)
    files = d['files']
    assert isinstance(files, list)
    return package_db_entry(descriptor, files)
  
  def to_json(self):
    return json.dumps(self.to_dict(), indent = 2, sort_keys = True)

  @classmethod
  def parse_json(clazz, s):
    return clazz.parse_dict(json.loads(s))
  
  def has_any_files(self, files):
    'Return True if we have any of the given files.'
    files = object_util.listify(files)
    for f in files:
      if f in self.files:
        return True
    return False


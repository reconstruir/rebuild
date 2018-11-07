#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat import StringIO
from bes.common import check, type_checked_list
from .package_descriptor import package_descriptor

class package_descriptor_list(type_checked_list):

  __value_type__ = package_descriptor
  
  def __init__(self, values = None):
    super(package_descriptor_list, self).__init__(values = values)

  def to_string(self, delimiter = '\n'):
    buf = StringIO()
    first = True
    for pd in iter(self):
      if not first:
        buf.write(delimiter)
      first = False
      buf.write(str(pd))
    return buf.getvalue()

  def __str__(self):
    return self.to_string()

  def names(self):
    'Return the names for all the descriptors.'
    return [ pd.name for pd in self ]

  def latest_versions(self):
    'Return a list of only the lastest version of any package with multiple versions.'
    latest = {}
    for pd in self:
      if not pd.name in latest:
        latest[pd.name] = pd
      else:
        if pd.version > latest[pd.name].version:
          latest[pd.name] = pd
    result = package_descriptor_list(latest.values())
    result.sort()
    return result

  @classmethod
  def resolve(clazz, what):
    if check.is_string(what):
      return clazz([ package_descriptor.parse(pkg_descs) ])
    elif check.is_string_seq(what):
      return clazz([ package_descriptor.parse(p) for p in what ])
    elif check.is_package_descriptor(what):
      return clazz([ what ])
    elif check.is_package_descriptor_seq(what):
      return what
    else:
      raise TypeError('Cannot resolve to package descriptor list: %s - %s' % (str(what), type(what)))
  
check.register_class(package_descriptor_list, include_seq = False)

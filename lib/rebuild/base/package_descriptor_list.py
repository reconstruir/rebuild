#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from .package_descriptor import package_descriptor

class package_descriptor_list(object):

  FOO = 'ununsed'

  '''
  @classmethod
  def sort_by_name(clazz, descriptors):
    'Sort a list of descriptors in ascending order using package info.'
    check.check_package_descriptor_seq(descriptors)
    return sorted(descriptors, cmp = package_descriptor.full_name_cmp)

  @classmethod
  def latest_versions(clazz, descriptors):
    'Return a list of only the lastest version of any package with multiple versions.'
    check.check_package_descriptor_seq(descriptors)
    descriptors = clazz.sort_by_full_name(descriptors)
    d = {}
    for package in descriptors:
      d[package.info.name] = package
    return clazz.sort_by_descriptor(d.values())

  @classmethod
  def filter_out_by_name(clazz, descriptors, name):
    'Return a list of only the descriptors that dont match name.'
    check.check_package_descriptor_seq(descriptors)
    return [ pd for pd in descriptors if pd.name != name ]
'''
  
#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat import StringIO
from bes.common import check, type_checked_list
from .package_descriptor import package_descriptor

class package_descriptor_list(type_checked_list):

  def __init__(self, values = None):
    super(package_descriptor_list, self).__init__(package_descriptor, values = values)

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
  
check.register_class(package_descriptor_list, include_seq = False)

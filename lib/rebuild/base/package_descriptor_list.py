#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat.StringIO import StringIO
from bes.common.check import check
from bes.common.type_checked_list import type_checked_list
from .package_descriptor import package_descriptor
from .requirement_list import requirement_list
from .requirement import requirement

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

  def names(self, include_version = False):
    'Return the names for all the descriptors.'
    if include_version:
      return [ pd.full_name for pd in self ]
    else:
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
    result.sort(key = lambda p: tuple(p))
    return result

  def filter_by_name(self, name):
    'Return a list of only those package descriptors whose name matches.'
    return package_descriptor_list([ pd for pd in self if pd.name == name ])

  def filter_by_requirement(self, req):
    'Return a list of only those package descriptors that match the given requirement.'
    check.check_requirement(req)
    result = package_descriptor_list()
    for pd in self:
      if pd.matches_requirement(req):
        result.append(pd)
    return result
  
  def to_requirement_list(self):
    'Return a list of requirement object for this package descriptor list.  Not this loses a bunch of info.'
    result = requirement_list()
    for pd in self:
      result.append(requirement(pd.name, '==', str(pd.version)))
    return result
  
check.register_class(package_descriptor_list, include_seq = False)

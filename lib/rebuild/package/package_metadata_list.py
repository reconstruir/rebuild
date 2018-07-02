#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, type_checked_list
from .package_metadata import package_metadata

class package_metadata_list(type_checked_list):

  __value_type__ = package_metadata
  
  def __init__(self, values = None):
    super(package_metadata_list, self).__init__(values = values)

  def latest_versions(self):
    'Return a list of only the lastest version of any package with multiple versions.'
    latest = {}
    for md in self:
      if not md.name in latest:
        latest[md.name] = md
      else:
        if md.build_version > latest[md.name].build_version:
          latest[md.name] = md
    result = package_metadata_list(latest.values())
    result.sort()
    return result
  
check.register_class(package_metadata_list, include_seq = False)

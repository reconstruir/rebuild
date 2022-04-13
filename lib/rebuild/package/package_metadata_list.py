#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.type_checked_list import type_checked_list
from bes.build.artifact_descriptor import artifact_descriptor
from .package_metadata import package_metadata

class package_metadata_list(type_checked_list):

  __value_type__ = package_metadata
  
  def __init__(self, values = None):
    super(package_metadata_list, self).__init__(values = values)

  def filter_by_name(self, name):
    'Return only the descriptors that match name.'
    return package_metadata_list([ md for md in self if md.name == name ])
  
  def filter_by_level(self, level):
    'Return only the descriptors that match level.'
    return package_metadata_list([ md for md in self if md.level == level ])
  
  def filter_by_system(self, system):
    'Return only the descriptors that match system.'
    return package_metadata_list([ md for md in self if md.system == system ])

  def filter_by_build_target(self, build_target):
    'Return only the descriptors that match system.'
    return package_metadata_list([ md for md in self if md.build_target == build_target ])
    
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

  @classmethod
  def parse_artifact_paths(self, paths):
    'Return an artifact_descriptor_list by parsing the list of artifact files.'
    result = package_metadata_list()
    for filename in paths:
      adesc = artifact_descriptor.parse_artifact_path(filename)
      md = package_metadata.make_from_artifact_descriptor(adesc, filename)
      result.append(md)
    return result
  
check.register_class(package_metadata_list, include_seq = False)

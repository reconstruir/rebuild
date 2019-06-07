#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat.StringIO import StringIO
from bes.common.check import check
from bes.common.type_checked_list import type_checked_list
from .artifact_descriptor import artifact_descriptor

class artifact_descriptor_list(type_checked_list):

  __value_type__ = artifact_descriptor
  
  def __init__(self, values = None):
    super(artifact_descriptor_list, self).__init__(values = values)

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

  def filter_by_name(self, name):
    'Return only the descriptors that match name.'
    return artifact_descriptor_list([ adesc for adesc in self if adesc.name == name ])
  
  def filter_by_level(self, level):
    'Return only the descriptors that match level.'
    return artifact_descriptor_list([ adesc for adesc in self if adesc.level == level ])
  
  def filter_by_system(self, system):
    'Return only the descriptors that match system.'
    return artifact_descriptor_list([ adesc for adesc in self if adesc.system == system ])

  def filter_by_build_target(self, build_target):
    'Return only the descriptors that match system.'
    return artifact_descriptor_list([ adesc for adesc in self if adesc.build_target == build_target ])

  def latest_versions(self):
    'Return a list of only the lastest version of any artifact with multiple versions.'
    latest = {}
    for adesc in self:
      name = adesc.name
      if not name in latest:
        latest[name] = adesc
      else:
        if adesc.build_version > latest[name].build_version:
          latest[name] = adesc
    result = artifact_descriptor_list(latest.values())
    result.sort(key = lambda adesc: tuple(adesc))
    return result

  @classmethod
  def parse_artifact_paths(self, paths):
    'Return an artifact_descriptor_list by parsing the list of artifact files.'
    return artifact_descriptor_list([ artifact_descriptor.parse_artifact_path(p.filename) for p in paths ])
    
check.register_class(artifact_descriptor_list, include_seq = False)

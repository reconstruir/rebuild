#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat import StringIO
from bes.common import check, type_checked_list
from .requirement import requirement
from .requirement_hardness import requirement_hardness
from .requirement_parser import requirement_parser
from .build_system import build_system

class requirement_list(type_checked_list):

  def __init__(self, values = None):
    super(requirement_list, self).__init__(requirement, values = values)

  @classmethod
  def cast_entry(clazz, entry):
    if isinstance(entry, tuple):
      return requirement(*entry)
    return entry
  
  def to_string(self, delimiter = ' '):
    buf = StringIO()
    first = True
    for req in iter(self):
      if not first:
        buf.write(delimiter)
      first = False
      buf.write(str(req))
    return buf.getvalue()

  def __str__(self):
    return self.to_string()

  @classmethod
  def parse(clazz, text, default_system_mask = None):
    reqs = clazz([ req for req in requirement_parser.parse(text, default_system_mask = default_system_mask) ])
    reqs.remove_dups()
    return reqs

  def resolve(self, system):
    'Resolve requirements for the given system.'
    if not build_system.system_is_valid(system):
      raise RuntimeError('Invalid system: %s' % (system))
    return requirement_list([ req for req in iter(self) if req.system_mask == None or build_system.mask_matches(req.system_mask, system) ])
  
  def filter_by_hardness(self, hardness):
    'Return only the requirements that match hardness.'
    return requirement_list([ req for req in self if req.hardness_matches(hardness) ])

  def filter_by_system(self, system):
    'Return only the requirements that match system.'
    return requirement_list([ req for req in self if req.system_mask_matches(system) ])

  def names(self):
    'Return only the requirements that match system.'
    return [ req.name for req in self ]

  '''
  def dependency_map(self, hardness, system):
    check.check_requirement_hardness_seq(descriptor)
    dep_map = {}
    for req in iter(self):
      
    for name, descriptor in self._packages.items():
      reqs = descriptor.caca_requirements.filter_by_hardness(hardness)


#    check.check_package_descriptor_seq(descriptors)
#    dep_map = {}
#    for pd in descriptors:
#      if pd.name in dep_map:
#        raise RuntimeError('already in dependency map: %s' % (pd.name))
      dep_map[pd.name] = pd.requirements_names | pd.build_tool_requirements_names | pd.build_requirements_names
    return dep_map
'''
  
check.register_class(requirement_list, include_seq = False)

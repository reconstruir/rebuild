#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat import StringIO
from bes.common import check, type_checked_list
from .requirement import requirement
from .requirement_hardness import requirement_hardness
from .requirement_parser import requirement_parser
from .build_system import build_system

class requirement_list(type_checked_list):

  __value_type__ = requirement
  
  def __init__(self, values = None):
    super(requirement_list, self).__init__(values = values)

  @classmethod
  def cast_value(clazz, entry):
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

  def __hash__(self):
    return hash(str(self))
  
  def __str__(self):
    return self.to_string()

  @classmethod
  def parse(clazz, text, default_system_mask = None):
    if check.is_string_seq(text):
      text = ' '.join(text)
    check.check_string(text)
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

  @staticmethod
  def _check_cast_func(clazz, obj):
    return clazz([ x for x in obj ])
  
check.register_class(requirement_list, include_seq = False, cast_func = requirement_list._check_cast_func)

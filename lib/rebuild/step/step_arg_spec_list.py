#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check_type
from bes.compat import StringIO
from bes.text import comments
from .step_arg_spec import step_arg_spec

class step_arg_spec_list(object):

  def __init__(self, specs = None):
    specs = specs or []
    self._specs = [ v for v in specs ]

  def __iter__(self):
    return iter(self._specs)

  def __getitem__(self, i):
    return self._specs[i]
  
  def __setitem__(self, i, spec):
    check_type.check_step_arg_spec(spec, 'spec')
    self._specs[i] = spec

  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self._specs == other._specs
    elif isinstance(other, list):
      return self._specs == other
    else:
      raise TypeError('other should be of step_arg_spec_list type instead of %s' % (type(other)))
    
  def __str__(self):
    buf = StringIO()
    for step in self._specs:
      buf.write(str(step))
      buf.write('\n')
    return buf.getvalue().strip()
    
  def append(self, spec):
    check_type.check_step_arg_spec(spec, 'spec')
    self._specs.append(step)

  def extend(self, specs):
    for spec in specs:
      self.append(spec)

  def __len__(self):
    return len(self._specs)

  @classmethod
  def parse(clazz, text):
    result = []
    text = comments.strip_multi_line(text, strip = True, remove_empties = False)
    lines = text.split('\n')
    for i, line in enumerate(lines):
      if line:
        result.append(step_arg_spec.parse(line, i + 1))
    return result
  
check_type.register_class(step_arg_spec_list, include_seq = False)

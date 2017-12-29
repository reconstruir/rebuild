#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from bes.compat import StringIO

class recipe_step_list(object):

  def __init__(self, steps = None):
    steps = steps or []
    self._steps = [ v for v in steps ]

  def __iter__(self):
    return iter(self._steps)

  def __getitem__(self, i):
    return self._steps[i]
  
  def __setitem__(self, i, step):
    check.check_recipe_step(step, 'step')
    self._steps[i] = step

  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self._steps == other._steps
    elif isinstance(other, list):
      return self._steps == other
    else:
      raise TypeError('other should be of recipe_step_list type instead of %s' % (type(other)))
    
  def __str__(self):
    buf = StringIO()
    for step in self._steps:
      buf.write(str(step))
      buf.write('\n')
    return buf.getvalue().strip()
    
  def append(self, step):
    check.check_recipe_step(step, 'step')
    self._steps.append(step)

  def extend(self, steps):
    for step in steps:
      self.append(step)

  def __len__(self):
    return len(self._steps)
  
check.register_class(recipe_step_list, include_seq = False)

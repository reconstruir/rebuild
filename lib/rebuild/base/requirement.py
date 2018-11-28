#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, object_util
from collections import namedtuple
from bes.compat import StringIO

from .build_system import build_system
from .requirement_hardness import requirement_hardness

class requirement(namedtuple('requirement', 'name,operator,version,system_mask,hardness')):

  def __new__(clazz, name, operator, version, system_mask = None, hardness = None):
    assert name
    assert name == str(name)
    name = str(name)
    if operator:
      assert operator == str(operator)
      operator = str(operator)
    if version:
      assert version == str(version)
      version = str(version)
    if system_mask:
      assert system_mask == str(system_mask)
      system_mask = str(system_mask)
    if hardness:
      hardness = requirement_hardness(hardness)
      check.check_requirement_hardness(hardness)
    return clazz.__bases__[0].__new__(clazz, name, operator, version, system_mask, hardness)

  def __str__(self):
    buf = StringIO()
    if self.hardness:
      buf.write(str(self.hardness))
      buf.write(' ')
    buf.write(self.name)
    if self.system_mask and self.system_mask != 'all':
      buf.write('(')
      buf.write(self.system_mask)
      buf.write(')')
    if self.operator:
      buf.write(' ')
      buf.write(self.operator)
      buf.write(' ')
      buf.write(self.version)
    return buf.getvalue()

  def to_string_colon_format(self):
    req_no_system_mask = self.clone_replace_system_mask(None)
    buf = StringIO()
    if self.system_mask:
      buf.write(self.system_mask)
    else:
      buf.write('all')
    buf.write(': ')
    buf.write(str(req_no_system_mask))
    return buf.getvalue()

  def clone_replace_hardness(self, hardness):
    l = list(self)
    l[4] = hardness
    return self.__class__(*l)
  
  def clone_replace_system_mask(self, system_mask):
    l = list(self)
    l[3] = system_mask
    return self.__class__(*l)

  def system_mask_matches(self, system):
    'Resolve requirements for the given system.'
    if not build_system.system_is_valid(system):
      raise ValueError('invalid system: %s - %s' % (str(system), type(system)))
    self_system_mask = self.system_mask or build_system.ALL
    return build_system.mask_matches(self_system_mask, system)

  def hardness_matches(self, hardness):
    'Return True if hardness matches.'
    hardness = object_util.listify(hardness)
    if not requirement_hardness.is_valid_seq(hardness):
      raise ValueError('invalid hardness: %s - %s' % (str(hardness), type(hardness)))
    self_hardness = self.hardness or requirement_hardness.DEFAULT
    for h in hardness:
      if self_hardness == requirement_hardness(h):
        return True
    return False
  
check.register_class(requirement)

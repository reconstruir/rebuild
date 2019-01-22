#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import check, variable
from bes.system import os_env_var

# From https://stackoverflow.com/questions/4037481/caching-attributes-of-classes-in-python
class env_resolving_property(object):
  """
  Descriptor (non-data) for building an attribute on-demand on first use.
  """
  def __init__(self, factory):
    """
    <factory> is called such: factory(instance) to build the attribute.
    """
    self._attr_name = factory.__name__
    self._factory = factory

  def __get__(self, instance, owner):
    # Build the attribute.
    attr = self._factory(instance)
    attr = self.resolve_value(attr)
    
    # Cache the value; hide ourselves.
    setattr(instance, self._attr_name, attr)

    return attr

  @classmethod
  def resolve_value(clazz, value):
    value = clazz.resolve_user(value)
    value = clazz.resolve_env_vars(value)
    return value
  
  @classmethod
  def resolve_user(clazz, value):
    if not check.is_string(value):
      return value
    if value.startswith('~/'):
      return path.expanduser(location)
    return value
  
  @classmethod
  def resolve_env_vars(clazz, value):
    if not check.is_string(value):
      return value
    variables = variable.find_variables(value)
    substitutions = {}
    for var in variables:
      os_var = os_env_var(var)
      if not os_var.is_set:
        raise ValueError('%s not set in the current environment: \"%s\"' % (var, value))
      substitutions[var] = os_var.value
    return variable.substitute(value, substitutions, word_boundary = True)
  
class credentials(object):

  def __init__(self, username, password):
    check.check_string(username)
    check.check_string(password)
    self._username = username
    self._password = password

  @env_resolving_property
  def username(self):
    return self._username
  
  @env_resolving_property
  def password(self):
    return self._password
  
check.register_class(credentials, include_seq = False)

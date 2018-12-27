#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import check, variable
from bes.system import os_env_var

class credentials(object):

  def __init__(self, username, password):
    check.check_string(username)
    check.check_string(password)
    self._username = username
    self._password = password

  @property
  def username(self):
    return self._resolve_variables(self._username)
  
  @username.setter
  def username(self, value):
    raise Exception('username is readonly')
  
  @property
  def password(self):
    return self._resolve_variables(self._password)
  
  @password.setter
  def password(self, value):
    raise Exception('password is readonly')

  def _resolve_variables(clazz, value):
    variables = variable.find_variables(value)
    substitutions = {}
    for var in variables:
      os_var = os_env_var(var)
      if not os_var.is_set:
        raise ValueError('%s not set in the current environment: \"%s\"' % (var, value))
      substitutions[var] = os_var.value
    return variable.substitute(value, substitutions, word_boundary = True)
  
check.register_class(credentials, include_seq = False)

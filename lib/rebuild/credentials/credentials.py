#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from os import path
from collections import namedtuple
from bes.common.check import check
from bes.common.variable import variable
from bes.property.env_var_property import env_var_property
from bes.compat.StringIO import StringIO

class credentials(object):

  def __init__(self, **kargs):
    self.__dict__['_credentials'] = {}
    self.set_attrs(kargs)
    
  def __str__(self):
    buf = StringIO()
    first = True
    for key, value in sorted(self.__dict__['_credentials'].items()):
      if not first:
        buf.write('; ')
      first = False
      buf.write('{}=**********'.format(key))
    return buf.getvalue()
    return '{}:{}'.format(self.username, '**********')
    
  def __getattr__(self, key):
    if not key in self.__dict__['_credentials']:
      raise KeyError('no such credential: {}'.format(key))
    value = self.__dict__['_credentials'][key]
    return env_var_property.resolve_value(value)

  def __setattr__(self, key, value):
    self.__dict__['_credentials'][key] = value

  def __eq__(self, other):
    check.check_credentials(other)
    return self.__dict__['_credentials'] == other.__dict__['_credentials']

  def set_attrs(self, values):
    for key, value in values.items():
      setattr(self, key, value)

  def to_dict(self):
    return copy.deepcopy(self.__dict__['_credentials'])

  def to_tuple(self, *keys):
    return tuple([ getattr(self, key) for key in keys ])

  @classmethod
  def make_credentials(clazz, **kargs):
    c = credentials()
    for key, value in kargs.items():
      setattr(c, key, value)
    return c
  
check.register_class(credentials, include_seq = False)

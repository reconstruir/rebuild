#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from os import path
from collections import namedtuple
from bes.common.check import check
from bes.common.variable import variable
from bes.property.env_var_property import env_var_property
from bes.compat.StringIO import StringIO

class credentials(object):

  def __init__(self, config_source, **kargs):
    self.__dict__['_credentials'] = {}
    self.__dict__['_config_source'] = config_source
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

  def __repr__(self):
    return str(self)
  
  def __getattr__(self, key):
    if not key in self.__dict__['_credentials']:
      raise KeyError('no such credential: {}'.format(key))
    value = self.__dict__['_credentials'][key]
    try:
      return env_var_property.resolve_value(value)
    except ValueError as ex:
      raise ValueError('{}: {}'.format(self.__dict__['_config_source'], str(ex)))

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

check.register_class(credentials, include_seq = False)

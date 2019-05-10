#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple
from bes.common import check, variable
from bes.property.env_var_property import env_var_property
from bes.compat import StringIO

class credentials(object):

  def __init__(self):
    self.__dict__['_credentials'] = {}

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

    
check.register_class(credentials, include_seq = False)
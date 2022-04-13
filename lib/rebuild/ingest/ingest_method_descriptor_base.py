#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.system.check import check

from collections import namedtuple

class ingest_method_descriptor_base(with_metaclass(ABCMeta, object)):
  
  @abstractmethod
  def method(self):
    pass

  @abstractmethod
  def fields(self):
    pass

  @abstractmethod
  def download(self, args):
    pass

  def required_field_keys(self):
    return set([ field.key for field in self.fields() if not field.optional ])
  
  @classmethod
  def _check_download_field(clazz, kargs, field, optional = False):
    if not field in kargs:
      if optional:
        return None
      raise KeyError('missing field: {}'.format(field))
    return kargs[field]

check.register_class(ingest_method_descriptor_base, name = 'ingest_method_descriptor')

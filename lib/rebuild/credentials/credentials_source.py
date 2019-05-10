#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from abc import abstractmethod, ABCMeta

from collections import namedtuple
from bes.common import check, variable
from bes.system import os_env
from bes.system.compat import with_metaclass

class credentials_source(with_metaclass(ABCMeta, object)):
  
  @abstractmethod
  def is_valid(self):
    pass

  @abstractmethod
  def credentials(self):
    pass
check.register_class(credentials_source)
  
class credentials_source_env(credentials_source):

  def __init__(self, username):
    
  
  @abstractmethod
  def is_valid(self):
    pass

  @abstractmethod
  def credentials(self):
    pass
check.register_class(credentials_source)

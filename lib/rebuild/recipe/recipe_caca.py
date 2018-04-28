#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.common import check

class recipe_caca(with_metaclass(ABCMeta, object)):
  
  def __init__(self, env):
    check.check_value_env(env)
    self.env = env
  
  @abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    pass

  @classmethod
  @abstractmethod
  def parse(self, env, recipe_filename, value):
    'Parse a value.'
    pass

check.register_class(recipe_caca)

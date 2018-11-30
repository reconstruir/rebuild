#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.common import check

from .hook_result import hook_result

class hook(with_metaclass(ABCMeta)):

  result = hook_result
  
  def __init__(self):
    'Create a new hook.'
    pass

  @abstractmethod
  def execute(self, script, env):
    'Execute the hook.  Same semantics as step.execute()'
    pass
    
check.register_class(hook)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from rebuild.step.step import step
from rebuild.step.step_result import step_result
from bes.system.os_env import os_env
from bes.system.env_var import os_env_var

class step_setup_prepare_environment(step):
  'Prepare the environment.'

  def __init__(self):
    super(step_setup_prepare_environment, self).__init__()

  #@abstractmethod
  @classmethod
  def define_args(clazz):
    return ''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    # We want a clean environment for tools to work
    unixpath_save = self._path_save('BESTEST_UNIXPATH')
    pythonpath_save = self._path_save('BESTEST_PYTHONPATH')
    os_env.path_reset()
    os_env_var('PATH').append(unixpath_save)
    os_env_var('PYTHONPATH').append(pythonpath_save)
    return step_result(True, None)

  @classmethod
  def _path_save(clazz, name):
    var = os_env_var(name)
    if not var.is_set:
      return []
    return var.path

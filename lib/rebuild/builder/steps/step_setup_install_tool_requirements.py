#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, os.path as path

from bes.system.os_env import os_env
from rebuild.step.step import step
from rebuild.step.step_result import step_result
from rebuild.base.build_blurb import build_blurb

class step_setup_install_tool_requirements(step):
  'Install package dependencies.'

  def __init__(self):
    super(step_setup_install_tool_requirements, self).__init__()

  #@abstractmethod
  @classmethod
  def define_args(clazz):
    return ''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    if env.config.is_partial_build:
      return step_result(True, 'skipping step_setup_install_tool_requirements because build is partial')
      
    package_desc = script.descriptor
    tools = script.resolve_deps(['TOOL'], False)
    build_blurb.blurb('rebuild', '%s - tool requirements: %s' % (package_desc.name, ' '.join([ t.name for t in tools ])))
    if not tools:
      message = 'No tools for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    env.tools_manager.ensure_tools(tools)
    env.tools_manager.expose_env(tools)
        
    return step_result(True, None)

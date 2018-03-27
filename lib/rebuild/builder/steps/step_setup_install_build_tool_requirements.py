#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, os.path as path

from rebuild.step import step, step_result
from rebuild.base import build_blurb

class step_setup_install_build_tool_requirements(step):
  'Install package dependencies.'

  def __init__(self):
    super(step_setup_install_build_tool_requirements, self).__init__()

  def execute(self, script, env, args):
    package_desc = script.descriptor
    tools = script.resolve_deps(['TOOL'], False)
    build_blurb.blurb('build', '%s - tool requirements: %s' % (package_desc.name, ' '.join([ t.name for t in tools ])))
    if not tools:
      message = 'No tools for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)
      
    env.update_tools(tools)
    return step_result(True, None)

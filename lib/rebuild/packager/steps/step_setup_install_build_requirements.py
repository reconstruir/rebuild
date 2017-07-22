#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, os.path as path

from rebuild.step_manager import Step, step_result
from rebuild import build_blurb

class step_setup_install_build_requirements(Step):
  'Install package dependencies.'

  def __init__(self):
    super(step_setup_install_build_requirements, self).__init__()

  def execute(self, argument):
    package_desc = argument.env.package_descriptor
    build_blurb.blurb('build', '%s - build_requirements: %s' % (package_desc.name, ' '.join([ t.name for t in package_desc.resolved_build_requirements ])))
    if not package_desc.resolved_build_requirements:
      message = 'No tools for %s' % (argument.env.package_descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)
    assert argument.env.rebbe
    argument.env.rebbe.update_tools(package_desc.resolved_build_requirements)
    return step_result(True, None)

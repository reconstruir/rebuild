#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.common import object_util
from rebuild.step import step, step_result
from rebuild.base import build_blurb

class step_setup_install_requirements(step):
  'Install package dependencies.'

  def __init__(self):
    super(step_setup_install_requirements, self).__init__()

  def execute(self, script, env, args):
    package_desc = script.descriptor
    build_blurb.blurb('build', '%s - requirements: %s' % (package_desc.name, ' '.join([ t.name for t in package_desc.resolved_requirements ])))
    
    if package_desc.resolved_requirements:
      script.requirements_manager.install_packages(package_desc.resolved_requirements,
                                                   script.build_target,
                                                   env.artifact_manager)
    else:
      message = 'No requirements for %s' % (script.descriptor.full_name)
      self.log_d(message)
      
    if package_desc.resolved_build_requirements:
      script.requirements_manager.install_packages(package_desc.resolved_build_requirements,
                                                   script.build_target,
                                                   env.artifact_manager)
    else:
      message = 'No build_requirements for %s' % (script.descriptor.full_name)
      self.log_d(message)
      
    return step_result(True, None)

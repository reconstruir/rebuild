#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.common.object_util import object_util
from rebuild.step.step import step
from rebuild.step.step_result import step_result
from rebuild.base.build_blurb import build_blurb

class step_setup_install_requirements(step):
  'Install package dependencies.'

  def __init__(self):
    super(step_setup_install_requirements, self).__init__()

  #@abstractmethod
  @classmethod
  def define_args(clazz):
    return ''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    if env.config.is_partial_build:
      return step_result(True, 'skipping step_install_requirements because build is partial')

    package_desc = script.descriptor
    requirements = env.requirement_manager.resolve_deps([package_desc.name],
                                                        env.config.build_target.system,
                                                        ['BUILD', 'RUN'],
                                                        False)
    build_blurb.blurb('rebuild', '%s - requirements: %s' % (package_desc.name, ' '.join([ p.name for p in requirements])))

    if not requirements:
      message = 'No requirements for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    script.requirements_manager.install_packages(requirements,
                                                 script.build_target, ['BUILD', 'RUN'])

    return step_result(True, None)

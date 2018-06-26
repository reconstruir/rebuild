#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.archive import archiver
from rebuild.step import compound_step, step
from rebuild.base import package_descriptor

class _step_combine_packages_unpack(step):
  'Install package dependencies.'

  @classmethod
  def define_args(clazz):
    return '''
    packages requirement_list
    '''
  
  def __init__(self):
    super(_step_combine_packages_unpack, self).__init__()

  #@abstractmethod
  def execute(self, script, env, values, inputs):
    packages = values.get('packages')
    for package in packages:
      pdesc = package_descriptor(package.name, package.version)
      pmeta = env.artifact_manager.find_by_package_descriptor(pdesc, env.config.build_target, relative_filename = False)
      self.blurb('Extracting %s to %s' % (path.relpath(pmeta.filename), path.relpath(script.stage_dir)))
      archiver.extract(pmeta.filename,
                       script.stage_dir,
                       exclude = [ 'metadata' ])
    return self.result(True)

class step_combine_packages(compound_step):
  'A step that combines other projects.'
  from .step_setup import step_setup
  from .step_post_install import step_post_install
  
  __steps__ = [
    _step_combine_packages_unpack,
    step_post_install,
  ]
  def __init__(self):
    super(step_combine_packages, self).__init__()

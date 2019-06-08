#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common.check import check
from bes.archive.archiver import archiver

from rebuild.step.compound_step import compound_step
from rebuild.step.step import step
from rebuild.step.step_result import step_result
from rebuild.base.package_descriptor import package_descriptor

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
    if env.config.is_partial_build:
      return step_result(True, None, outputs = { '_skip_rest': True })

    packages = values.get('packages')
    archives = self._filenames(env, packages)
    common_files = self._common_files(archives)
    if common_files:
      return self.result(False, 'conflicting files found between artifacts: %s' % (' '.join(common_files)))
    for archive in archives:
      self.blurb('Extracting %s to %s' % (path.relpath(archive), path.relpath(script.stage_dir)))
      archiver.extract(archive,
                       script.stage_dir,
                       exclude = [ 'metadata/metadata.json' ])
    return self.result(True)

  @classmethod
  def _filenames(clazz, env, packages):
    filenames = []
    for package in packages:
      pdesc = package_descriptor(package.name, package.version)
      pmeta = env.artifact_manager.find_by_package_descriptor(pdesc, env.config.build_target, relative_filename = False)
      filenames.append(pmeta.filename)
    return filenames

  @classmethod
  def _common_files(clazz, archives):
    common_files = archiver.common_files(archives)
    common_files.remove('metadata/metadata.json')
    return common_files

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

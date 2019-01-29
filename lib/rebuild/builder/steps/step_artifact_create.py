#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.common import check, dict_util
from bes.archive import archiver
from bes.key_value import key_value_list
from bes.fs import file_util
from bes.common import dict_util
from rebuild.step import compound_step, step, step_result
from rebuild.package import package, package_tester

class step_artifact_create_make_package(step):
  'Make a package from the state_dir.'

  def __init__(self):
    super(step_artifact_create_make_package, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    build_target_distro string
    '''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    
    if not script.has_stage_dir():
      return step_result(False, script.format_message('No files to package found in {stage_dir}'))

    if False:
    #if '_REBUILD_UPSTREAM_VERSION_OVERRIDE' in inputs:
      version = script.descriptor.version.clone(mutations = { 'upstream_version': inputs['_REBUILD_UPSTREAM_VERSION_OVERRIDE'],
                                                              'revision': 0 })
      descriptor = script.descriptor.clone(mutations = { 'version': version })
    else:
      descriptor = script.descriptor

    output_tarball_path = path.join(script.artifact_dir, descriptor.tarball_filename)
    build_target_mutations = {}
    build_target_distro = values.get('build_target_distro')
    if build_target_distro:
      if build_target_distro == 'none':
        build_target_mutations['distro_version_major'] = 'none'
        build_target_mutations['distro_version_minor'] = 'none'
      build_target_mutations['distro'] = build_target_distro
    bt = script.build_target.clone(mutations = build_target_mutations)
    self.blurb('creating tarball %s from %s' % (path.relpath(output_tarball_path), path.relpath(script.stage_dir)), fit = True)
    staged_tarball, metadata = package.create_package(output_tarball_path,
                                                      descriptor,
                                                      bt,
                                                      script.stage_dir)
    self.blurb('staged tarball: %s' % (path.relpath(staged_tarball)))
    outputs = {
      'staged_tarball': staged_tarball,
      'metadata': metadata,
    }
    return step_result(True, None, outputs = outputs)
  
class step_artifact_create_test_package(step):
  'Test an package with any tests give for it in its rebuildfile.'

  def __init__(self):
    super(step_artifact_create_test_package, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    tests file_list
    package_test_env key_values
    '''
  
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    tests = values.get('tests')
    package_test_env = values.get('package_test_env')
    
    if not tests:
      message = 'No tests for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    if env.config.no_tests:
      message = '%s: Skipping tests because of --no-tests' % (script.descriptor.full_name)
      self.blurb(message)
      return step_result(True, message)
      
    staged_tarball = inputs.get('staged_tarball', None)
    if not staged_tarball or not path.isfile(staged_tarball):
      message = 'Missing staged tarball for %s: ' % (str(script.descriptor))
      self.log_d(message)
      return step_result(False, message)

    for test in tests:
      check.check_value_file(test)
      config = package_tester.test_config(script,
                                          staged_tarball,
                                          env.artifact_manager,
                                          env.tools_manager,
                                          dict_util.combine(package_test_env.to_dict(), env.variable_manager.variables))
      tester = package_tester(config, test.filename)
      result =  tester.run()
      if not result.success:
        return result
    return step_result(True, None)

class step_artifact_create_publish_package(step):
  'Publish the package created by step_artifact_create_make_package.'

  def __init__(self):
    super(step_artifact_create_publish_package, self).__init__()

  #@abstractmethod
  def execute(self, script, env, values, inputs):
    staged_tarball = inputs.get('staged_tarball', None)
    if not staged_tarball or not path.isfile(staged_tarball):
      message = 'Missing staged tarball for %s: ' % (str(script.descriptor))
      self.log_d(message)
      return step_result(False, message)
    metadata = inputs.get('metadata', None)
    if not metadata:
      message = 'Missing metadata for %s: ' % (str(script.descriptor))
      self.log_d(message)
      return step_result(False, message)
    assert archiver.is_valid(staged_tarball)
    published_tarball = env.artifact_manager.publish(staged_tarball, True, metadata)
    self.blurb('published tarball locally: %s' % (path.relpath(published_tarball)))
    return step_result(True, None, outputs = { 'published_tarball': published_tarball })

class step_artifact_create(compound_step):
  'A collection of multiple cleanup steps.'
  __steps__ = [
    step_artifact_create_make_package,
    step_artifact_create_test_package,
    step_artifact_create_publish_package,
  ]
  def __init__(self):
    super(step_artifact_create, self).__init__()

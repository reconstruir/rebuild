#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.archive import archiver
from bes.fs import file_util
from rebuild.step import compound_step, step, step_result
from rebuild.package import package_tester

class step_artifact_create_make_package(step):
  'Make a package from the state_dir.'

  def __init__(self):
    super(step_artifact_create_make_package, self).__init__()

  def execute(self, script, env, args):
    assert 'output_tarball_path' in args
    staged_tarball = script.requirements_manager.create_package(args['output_tarball_path'],
                                                                script.descriptor,
                                                                script.build_target,
                                                                script.stage_dir,
                                                                script.env_dir)
    self.blurb('staged tarball: %s' % (staged_tarball))
    return step_result(True, None, output = { 'staged_tarball': staged_tarball })
  
  @classmethod
  def _default_output_tarball_path(clazz, script):
    tarball_name = '%s.tar.gz' % (script.descriptor.full_name)
    assert tarball_name == script.descriptor.tarball_filename
    return path.join(script.artifact_stage_dir, script.descriptor.tarball_filename)

  @classmethod
  def parse_step_args(clazz, script, env, args):
    output_tarball_path = args.get('output_tarball_path', None)
    if not output_tarball_path:
      output_tarball_path = clazz._default_output_tarball_path(script)
    output_artifact_path = env.artifact_manager.artifact_path(script.descriptor, script.build_target)
    return { 
      'output_tarball_path': output_tarball_path,
      'output_artifact_path': output_artifact_path,
    }

class step_artifact_create_check_package(step):
  'Check that the staged package is good.'

  def __init__(self):
    super(step_artifact_create_check_package, self).__init__()

  def execute(self, script, env, args):
    staged_tarball = args.get('staged_tarball', None)
    assert staged_tarball
    assert archiver.is_valid(staged_tarball)
    unpack_dir = path.join(script.check_dir, 'unpacked')
    archiver.extract(staged_tarball, unpack_dir, strip_common_base = True)

    for check_class in args.get('checks', []):
      check = check_class()
      check_result = check.check(path.join(unpack_dir, 'files'), script)
      if not check_result.success:
        return step_result(False, check_result.message)
    return step_result(True, None)

class step_artifact_create_test_package(step):
  'Test an package with any tests give for it in its rebuildfile.'

  def __init__(self):
    super(step_artifact_create_test_package, self).__init__()

  @classmethod
  def argspec(clazz):
    return {
      'tests': clazz.STRING_LIST,
    }
    
  def execute(self, script, env, args):
    if env.config.skip_tests:
      message = '%s: Skipping tests because of --skip-tests' % (script.descriptor.full_name)
      self.blurb(message)
      return step_result(True, message)
      
    tests = args.get('tests', [])
    if not tests:
      message = 'No tests for %s' % (script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    staged_tarball = args.get('staged_tarball', None)
    if not staged_tarball or not path.isfile(staged_tarball):
      message = 'Missing staged tarball for %s: ' % (str(script.descriptor))
      self.log_d(message)
      return step_result(False, message)
      
    for test in tests:
      config = package_tester.test_config(staged_tarball,
                                          script.source_dir,
                                          script.test_dir,
                                          env.artifact_manager,
                                          env.tools_manager,
                                          script.build_target)
      tester = package_tester(config, test)
      result =  tester.run()
      if not result.success:
        return result
    return step_result(True, None)

  def sources_keys(self):
    return [ 'tests' ]

  @classmethod
  def parse_step_args(clazz, script, env, args):
    return clazz.resolve_step_args_files(script, args, 'tests')

class step_artifact_create_publish_package(step):
  'Publish the package created by step_artifact_create_make_package.'

  def __init__(self):
    super(step_artifact_create_publish_package, self).__init__()

  def execute(self, script, env, args):
    staged_tarball = args.get('staged_tarball', None)
    assert staged_tarball
    assert archiver.is_valid(staged_tarball)
    published_tarball = env.artifact_manager.publish(staged_tarball, script.build_target)
    self.blurb('published tarball: %s' % (published_tarball))
    return step_result(True, None, output = { 'published_tarball': published_tarball })

class step_artifact_create(compound_step):
  'A collection of multiple cleanup steps.'
  __steps__ = [
    step_artifact_create_make_package,
    step_artifact_create_check_package,
    step_artifact_create_test_package,
    step_artifact_create_publish_package,
  ]
  def __init__(self):
    super(step_artifact_create, self).__init__()

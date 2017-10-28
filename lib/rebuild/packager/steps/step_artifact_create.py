#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path

from bes.archive import archiver
from bes.fs import file_util
from rebuild.step_manager import multiple_steps, Step, step_result
from rebuild.package_manager import package_tester

class step_artifact_create_make_package(Step):
  'Make a package from the state_dir.'

  def __init__(self):
    super(step_artifact_create_make_package, self).__init__()

  def execute(self, argument):
    assert 'output_tarball_path' in argument.args
    staged_tarball = argument.script.requirements_manager.create_package(argument.args['output_tarball_path'],
                                                                      argument.script.descriptor,
                                                                      argument.script.env.config.build_target,
                                                                      argument.script.stage_dir)
    self.blurb('staged tarball: %s' % (staged_tarball))
    return step_result(True, None, output = { 'staged_tarball': staged_tarball })

  @classmethod
  def _default_output_tarball_path(clazz, script, args):
    tarball_name = '%s.tar.gz' % (script.descriptor.full_name)
    assert tarball_name == script.descriptor.tarball_filename
    return path.join(script.artifact_stage_dir, script.descriptor.tarball_filename)

  @classmethod
  def parse_step_args(clazz, script, args):
    output_tarball_path = args.get('output_tarball_path', None)
    if not output_tarball_path:
      output_tarball_path = clazz._default_output_tarball_path(script, args)
    output_artifact_path = script.env.artifact_manager.artifact_path(script.descriptor, script.env.config.build_target)
    return { 
      'output_tarball_path': output_tarball_path,
      'output_artifact_path': output_artifact_path,
    }

class step_artifact_create_check_package(Step):
  'Check that the staged package is good.'

  def __init__(self):
    super(step_artifact_create_check_package, self).__init__()

  def execute(self, argument):
    staged_tarball = argument.output.get('staged_tarball', None)
    assert staged_tarball
    assert archiver.is_valid(staged_tarball)
    unpack_dir = path.join(argument.script.check_dir, 'unpacked')
    archiver.extract(staged_tarball, unpack_dir, strip_common_base = True)

    for check_class in argument.args.get('checks', []):
      check = check_class()
      check_result = check.check(path.join(unpack_dir, 'files'), argument.script)
      if not check_result.success:
        return step_result(False, check_result.message)
    return step_result(True, None)

class step_artifact_create_test_package(Step):
  'Test an package with any tests give for it in its rebuildfile.'

  def __init__(self):
    super(step_artifact_create_test_package, self).__init__()

  def execute(self, argument):
    if argument.script.env.config.skip_tests:
      message = '%s: Skipping tests because of --skip-tests' % (argument.script.descriptor.full_name)
      self.blurb(message)
      return step_result(True, message)
      
    tests = argument.args.get('tests', [])
    if not tests:
      message = 'No tests for %s' % (argument.script.descriptor.full_name)
      self.log_d(message)
      return step_result(True, message)

    staged_tarball = argument.output.get('staged_tarball', None)
    if not staged_tarball or not path.isfile(staged_tarball):
      message = 'Missing staged tarball for %s: ' % (str(argument.script.descriptor))
      self.log_d(message)
      return step_result(False, message)
      
    for test in tests:
      config = package_tester.test_config(staged_tarball,
                                          argument.script.source_dir,
                                          argument.script.test_dir,
                                          argument.script.env.artifact_manager,
                                          argument.script.env.tools_manager,
                                          argument.script.env.config.build_target)
      tester = package_tester(config, test)
      result =  tester.run() #self.__run_test(config, test)
      if not result.success:
        return result
    return step_result(True, None)

  def sources_keys(self):
    return [ 'tests' ]

  @classmethod
  def parse_step_args(clazz, script, args):
    return clazz.resolve_step_args_files(script, args, 'tests')

class step_artifact_create_publish_package(Step):
  'Publish the package created by step_artifact_create_make_package.'

  def __init__(self):
    super(step_artifact_create_publish_package, self).__init__()

  def execute(self, argument):
    staged_tarball = argument.output.get('staged_tarball', None)
    assert staged_tarball
    assert archiver.is_valid(staged_tarball)
    published_tarball = argument.script.env.artifact_manager.publish(staged_tarball, argument.script.env.config.build_target)
    self.blurb('published tarball: %s' % (published_tarball))
    return step_result(True, None, output = { 'published_tarball': published_tarball })

class step_artifact_create(multiple_steps):
  'A collection of multiple cleanup steps.'
  step_classes = [
    step_artifact_create_make_package,
    step_artifact_create_check_package,
    step_artifact_create_test_package,
    step_artifact_create_publish_package,
  ]
  def __init__(self):
    super(step_artifact_create, self).__init__()

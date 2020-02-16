#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common.check import check
from rebuild.step.compound_step import compound_step
from rebuild.step.step import step
from rebuild.step.step_result import step_result

class step_xcodebuild_build(step):
  'Configure Setup.'

  def __init__(self):
    super(step_xcodebuild_build, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    xcode_flags   string_list
    xcode_env     key_values
    project       string
    configuration string
    scheme        string
    '''
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    xcode_env = values.get('xcode_env')
    xcode_flags = values.get('xcode_flags')
    project = values.get('project')
    scheme = values.get('scheme')
    configuration = values.get('configuration')

    if not project:
      return self.result(False, 'No project given for %s' % (script.descriptor.full_name))

    if not scheme:
      return self.result(False, 'No scheme given for %s' % (script.descriptor.full_name))

    if not configuration:
      return self.result(False, 'No configuration given for %s' % (script.descriptor.full_name))

    if check.is_string_list(xcode_flags):
      xcode_flags = xcode_flags.to_list()
    else:
      assert isinstance(xcode_flags, list)

    derived_data_path = path.join(script.build_dir, 'derived_data')

    project_path = path.join(script.source_unpacked_dir, project)

    cmd = [
      'xcodebuild',
      '-configuration', configuration,
      '-scheme', scheme,
      '-derivedDataPath', derived_data_path,
      '-project', project_path,
    ]
    if env.config.verbose:
      cmd.append('-verbose')
    cmd.extend(xcode_flags)
    self.blurb_verbose('Calling: %s' % (' '.join(cmd)))
    return self.call_shell(cmd, script, env,
                           shell_env = xcode_env) #,
                           #save_logs = [ 'XcodeFiles/XcodeError.log', 'XcodeFiles/XcodeOutput.log' ])

class step_xcodebuild(compound_step):
  'A complete step to build xcode projects.'
  from .step_make import step_make
  from .step_setup import step_setup
  from .step_post_install import step_post_install
  
  __steps__ = [
    step_setup,
    step_xcodebuild_build,
    step_post_install,
  ]
  def __init__(self):
    super(step_xcodebuild, self).__init__()

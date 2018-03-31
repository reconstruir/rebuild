#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.step import compound_step, step, step_result
from bes.python import setup_tools
from bes.common import string_util, time_util 
from bes.version import version_info

class step_python_egg_build(step):
  'A step to do the "bdist_egg" target of setuptools.'

  DEFAULT_SETUP_SCRIPT = 'setup.py'
  
  def __init__(self):
    super(step_python_egg_build, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    shell_flags         string_list
    shell_env           key_values
    update_version_tag  string
    tarball_address     string_list
    setup_script        string       setup.py
    setup_dir           string
    '''
    
  def execute(self, script, env, args):
    values = self.recipe.resolve_values(env.config.build_target.system)
    shell_flags = values.get('shell_flags')
    shell_env = values.get('shell_env')
    update_version_tag = values.get('update_version_tag')
    tarball_address = values.get('tarball_address')
    setup_script = values.get('setup_script')
    setup_dir = values.get('setup_dir')
    
    if update_version_tag:
      assert tarball_address
      filename = path.join(script.build_dir, update_version_tag)
      assert path.isfile(filename)
      v1 = version_info.read_file(filename)
      v2 = v1.change(address = tarball_address[0], tag = tarball_address[1], timestamp = time_util.timestamp(timezone = True))
      v2.save_file(filename)
    
    cmd = '${PYTHON} %s bdist_egg --plat-name=${REBUILD_PYTHON_PLATFORM_NAME}' % (setup_script)
    return self.call_shell(cmd, script, env, args, extra_env = shell_env, execution_dir = setup_dir)

class step_python_egg_install(step):
  'Install the egg file produced by step_bdist_egg_build.'

  def __init__(self):
    super(step_python_egg_install, self).__init__()

  def execute(self, script, env, args):
    setup_dir = args.get('setup_dir', None)
    if setup_dir:
      dist_dir = path.join(script.build_dir, setup_dir, 'dist')
    else:
      dist_dir = path.join(script.build_dir, 'dist')
    eggs = setup_tools.list_eggs(dist_dir)
    if len(eggs) == 0:
      return step_result(False, 'No eggs found in %s' % (dist_dir))
    elif len(eggs) > 1:
      return step_result(False, 'Too many eggs found in %s' % (dist_dir))
    egg = path.join(dist_dir, eggs[0])
    mkdir_cmd = 'mkdir -p ${REBUILD_STAGE_PYTHON_LIB_DIR}'
    easy_install_cmd_parts = [
#      'rebbe_third_party_easy_install-${REBUILD_PYTHON_VERSION}',
      'rebbe_easy_install-${REBUILD_PYTHON_VERSION}',
      '--install-dir=${REBUILD_STAGE_PYTHON_LIB_DIR}',
      '--prefix=${REBUILD_STAGE_PREFIX_DIR}',
      '--no-deps',
      egg,
    ]
    easy_install_cmd = ' '.join(easy_install_cmd_parts)
    cmd_parts = [ mkdir_cmd, easy_install_cmd ]
    cmd = ' && '.join(cmd_parts)
    return self.call_shell(cmd, script, env, args)

class step_python_egg_check_downloaded_dependencies(step):
  'Check that the egg build and install process does not Install the egg file produced by step_bdist_egg_build.'

  def __init__(self):
    super(step_python_egg_check_downloaded_dependencies, self).__init__()

  def execute(self, script, env, args):
    setup_dir = args.get('setup_dir', None)
    if setup_dir:
      eggs_build_dir = path.join(script.build_dir, setup_dir, '.eggs')
    else:
      eggs_build_dir = path.join(script.build_dir, '.eggs')
    if not path.exists(eggs_build_dir):
      return step_result(True)
    eggs = setup_tools.list_eggs(eggs_build_dir)
    if len(eggs) == 0:
      return step_result(True)
    egg_names = [ path.basename(egg) for egg in eggs ]
    return step_result(False, 'Python downloaded dependency eggs: %s' % (' '.join(egg_names)))

class step_python_egg(compound_step):
  'A complete step to make python eggs using the "bdist_egg" target of setuptools.'
  from .step_setup import step_setup
  from .step_post_install import step_post_install

  __step_global_args__ = {
    #'FUCKFUCKFUCKFUCKFUCKFUCKFUCKFUCKFUCKFUCKFUCKFUCKFUCKFUCKFUCK': 666,
    #'copy_source_to_build_dir': True,
  }
  
  __steps__ = [
    step_setup,
    step_python_egg_build,
    step_python_egg_install,
    step_python_egg_check_downloaded_dependencies,
    step_post_install,
  ]

  def __init__(self):
    super(step_python_egg, self).__init__()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from package import package
#from package_db import package_db

import os, os.path as path
from collections import namedtuple

from rebuild.step import step_result
from rebuild.package_manager import package, package_manager
from rebuild.base import build_blurb, build_os_env, build_target
from rebuild.toolchain import toolchain
from rebuild.dependency import dependency_resolver
from bes.common import Shell
from bes.fs import file_replace

class package_tester(object):

  test_config = namedtuple('test_config', 'package_tarball,source_dir,test_dir,artifact_manager,tools_manager,build_target')

  def __init__(self, config, test):
    self._config = config
    self._test = test

  def run(self):
    rv = self.__run_test(self._config, self._test)
    return rv

  @classmethod
  def __run_test(clazz, config, test):
    build_blurb.blurb('tester', 'Testing %s with %s' % (config.package_tarball, test))
    assert path.isfile(test)
    tc = toolchain.get_toolchain(config.build_target)
    ce = tc.compiler_environment()
    compiler_flags = tc.compiler_flags()
    if test.endswith('.cpp'):
      return clazz.__run_c_test(config, test, ce['CXX'], compiler_flags['CXXFLAGS'])
    if test.endswith('.c'):
      return clazz.__run_c_test(config, test, ce['CC'], compiler_flags['CFLAGS'])
    elif test.endswith('.py'):
      return clazz.__run_python_test(config, test)
    elif test.endswith('.pl'):
      return clazz.__run_perl_test(config, test)
    elif test.endswith('.sh'):
      return clazz.__run_shell_test(config, test)
    else:
      raise RuntimeError('Uknown test type for %s: %s' % (config.package_info.name, test))

  @classmethod
  def __run_c_test(clazz, config, test_source, compiler, extra_cflags):
    setup = clazz.__setup_test(config, test_source)
    build_blurb.blurb_verbose('tester', '%s: running c test %s with %s' % (setup.package_info.name, test_source, compiler))
    package_names_for_pkg_config = [ setup.package_info.name ]

    # FIXME: static is hardcoded here (depends on global static mode)
    cflags, libs = setup.package_manager.compilation_flags(package_names_for_pkg_config, static = True)
    test_exe = path.join(setup.test_dir, setup.test_name + '.exe')
    cflags += extra_cflags
    cflags_flat = ' '.join(cflags)
    libs_flat = ' '.join(libs)
    compilation_cmd = '%s -o %s %s %s %s' % (compiler,
                                             test_exe,
                                             setup.test_source_with_replacements,
                                             cflags_flat,
                                             libs_flat)
    build_blurb.blurb_verbose('tester', '%s: compilation_cmd=\"%s\"' % (setup.package_info.name, compilation_cmd))
    build_blurb.blurb_verbose('tester', '%s: cflags=\"%s\" libs=\"%s\"' % (setup.package_info.name, cflags_flat, libs_flat))

    # Build the test
    rv = Shell.execute(compilation_cmd,
                       env = setup.env,
                       non_blocking = build_blurb.verbose,
                       stderr_to_stdout = True,
                       raise_error = False)
    if rv.exit_code != 0:
      return step_result(rv.exit_code == 0, rv.stdout)
    # Run the test
    rv = Shell.execute(test_exe, env = setup.env, non_blocking = build_blurb.verbose,
                       stderr_to_stdout = True, raise_error = False)

    # Restore the environment cause __setup_test() hacks it
    os.environ = setup.saved_env

    if rv.exit_code != 0:
      return step_result(rv.exit_code == 0, rv.stdout)
    
    return step_result(True, None)

  @classmethod
  def __run_python_test(clazz, config, test_source):
    setup = clazz.__setup_test(config, test_source)
    build_blurb.blurb_verbose('tester', '%s: running python test %s' % (setup.package_info.name, test_source))
    # FIXME: move this to setup
    setup.env['PYTHONPATH'] = setup.package_manager.python_lib_dir
    # Run the test
    cmd = 'python2.7 %s' % (setup.test_source_with_replacements)
    rv = Shell.execute(cmd, env = setup.env, non_blocking = build_blurb.verbose,
                       stderr_to_stdout = True, raise_error = False)
    if rv.exit_code != 0:
      return step_result(rv.exit_code == 0, rv.stdout)
    return step_result(True, None)

  @classmethod
  def __run_shell_test(clazz, config, test_source):
    return clazz.__run_exe_test('SHELL', 'bash', config, test_source)

  @classmethod
  def __determine_exe(clazz, env_var_name, default_exe):
    return os.environ.get(env_var_name, default_exe)
  
  @classmethod
  def __run_perl_test(clazz, config, test_source):
    return clazz.__run_exe_test('PERL', 'perl', config, test_source)

  __test_setup = namedtuple('__test_setup','package_info,env,saved_env,test_dir,test_name,test_source_with_replacements,package_manager')

  @classmethod
  def __setup_test(clazz, config, test_source):
    test_name = path.splitext(path.basename(test_source))[0]
    test_root_dir = path.join(config.test_dir, test_name)
    pm_root_dir = path.join(test_root_dir, 'requirements')

    pm = package_manager(pm_root_dir)

    package = pm.load_tarball(config.package_tarball, config.build_target, config.artifact_manager)
    pd = package.info
    
    deps_packages = pd.resolved_requirements
    all_packages = deps_packages + [ pd ]

    pm.install_packages(deps_packages, config.build_target, config.artifact_manager)
    pm.install_tarball(config.package_tarball)

    config.tools_manager.update(pd.resolved_build_requirements, config.artifact_manager)

    saved_env = build_os_env.clone_current_env()

    config.tools_manager.export_variables_to_current_env(pd.resolved_build_requirements)
    pm.export_variables_to_current_env(all_packages)

    shell_env = build_os_env.make_clean_env()
    build_os_env.update(shell_env, config.tools_manager.shell_env(pd.resolved_build_requirements), prepend = True)
    build_os_env.update(shell_env, pm.shell_env(all_packages), prepend = True)

    test_source_with_replacements = path.join(test_root_dir, path.basename(test_source))
    replacements = {
      'REBUILD_PACKAGER_SOURCE_DIR': config.source_dir,
      'REBUILD_PACKAGER_TEST_DIR': config.test_dir,
      'REBUILD_PACKAGER_TEST_NAME': test_name,
    }
    file_replace.copy_with_substitute(test_source, test_source_with_replacements,
                                      replacements, backup = False)
    return clazz.__test_setup(package.info, shell_env, saved_env,
                              test_root_dir, test_name,
                              test_source_with_replacements,
                              pm)

  @classmethod
  def __run_exe_test(clazz, exe_env_name, exe_default, config, test_source):
    setup = clazz.__setup_test(config, test_source)
    build_blurb.blurb_verbose('tester', '%s: running shell test %s' % (setup.package_info.name, test_source))
    exe = clazz.__determine_exe(exe_env_name, exe_default)
    cmd = '%s %s' % (exe, setup.test_source_with_replacements)
    rv = Shell.execute(cmd, env = setup.env, non_blocking = build_blurb.verbose,
                       stderr_to_stdout = True, raise_error = False)
    os.environ = setup.saved_env
    if rv.exit_code != 0:
      return step_result(rv.exit_code == 0, rv.stdout)
    return step_result(True, None)

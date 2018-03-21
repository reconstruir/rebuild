#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from package import package
#from package_db import package_db

import os, os.path as path
from collections import namedtuple

from rebuild.step import step_result
from rebuild.base import build_blurb, build_target
from rebuild.toolchain import toolchain
from bes.dependency import dependency_resolver
from bes.common import variable
from bes.system import execute, os_env
from bes.fs import file_replace

from .package import package
from .package_manager import package_manager

class package_tester(object):

  test_config = namedtuple('test_config', 'script,package_tarball,artifact_manager,tools_manager,extra_env')

  def __init__(self, config, test):
    self._config = config
    self._test = test

  def run(self):
    rv = self._run_test(self._config, self._test)
    return rv

  @classmethod
  def _run_test(clazz, config, test):
    build_blurb.blurb('tester', 'Testing %s with %s' % (path.relpath(config.package_tarball), test))
    assert path.isfile(test)
    tc = toolchain.get_toolchain(config.script.build_target)
    ce = tc.compiler_environment()
    compiler_flags = tc.compiler_flags()
    if test.endswith('.cpp'):
      return clazz._run_c_test(config, test, ce['CXX'], compiler_flags['CXXFLAGS'])
    if test.endswith('.c'):
      return clazz._run_c_test(config, test, ce['CC'], compiler_flags['CFLAGS'])
    elif test.endswith('.py'):
      return clazz._run_python_test(config, test)
    elif test.endswith('.pl'):
      return clazz._run_perl_test(config, test)
    elif test.endswith('.sh'):
      return clazz._run_shell_test(config, test)
    else:
      raise RuntimeError('Uknown test type for %s: %s' % (config.package_info.name, test))

  @classmethod
  def _run_c_test(clazz, config, test_source, compiler, extra_cflags):
    context = clazz._make_test_context(config, test_source)
    build_blurb.blurb_verbose('tester', '%s: running c test %s with %s' % (context.package_info.name, test_source, compiler))
    package_names_for_pkg_config = [ context.package_info.name ]

    # FIXME: static is hardcoded here (depends on global static mode)
    cflags, libs = context.package_manager.compilation_flags(package_names_for_pkg_config, static = True)
    test_exe = path.join(context.test_dir, context.test_name + '.exe')
    cflags += extra_cflags
    cflags_flat = ' '.join(cflags)
    libs_flat = ' '.join(libs)
    compilation_cmd = '%s -o %s %s %s %s' % (compiler,
                                             test_exe,
                                             context.test_source_with_replacements,
                                             cflags_flat,
                                             libs_flat)
    build_blurb.blurb_verbose('tester', '%s: compilation_cmd=\"%s\"' % (context.package_info.name, compilation_cmd))
    build_blurb.blurb_verbose('tester', '%s: cflags=\"%s\" libs=\"%s\"' % (context.package_info.name, cflags_flat, libs_flat))

    # Build the test
    rv = execute.execute(compilation_cmd,
                         env = context.env,
                         non_blocking = build_blurb.verbose,
                         stderr_to_stdout = True,
                         raise_error = False)
    if rv.exit_code != 0:
      return step_result(rv.exit_code == 0, rv.stdout)
    # Run the test
    rv = execute.execute(test_exe, env = context.env, non_blocking = build_blurb.verbose,
                         stderr_to_stdout = True, raise_error = False)

    # Restore the environment cause _make_test_context() hacks it
    os.environ = context.saved_env

    if rv.exit_code != 0:
      return step_result(rv.exit_code == 0, rv.stdout)
    
    return step_result(True, None)

  @classmethod
  def _run_python_test(clazz, config, test_source):
    context = clazz._make_test_context(config, test_source)
    build_blurb.blurb_verbose('tester', '%s: running python test %s' % (context.package_info.name, test_source))
    # FIXME: move this to context
    context.env['PYTHONPATH'] = context.package_manager.python_lib_dir
    # Run the test
    cmd = 'python2.7 %s' % (context.test_source_with_replacements)
    rv = execute.execute(cmd, env = context.env, non_blocking = build_blurb.verbose,
                         stderr_to_stdout = True, raise_error = False)
    if rv.exit_code != 0:
      return step_result(rv.exit_code == 0, rv.stdout)
    return step_result(True, None)

  @classmethod
  def _run_shell_test(clazz, config, test_source):
    return clazz._run_exe_test('SHELL', 'bash', config, test_source)

  @classmethod
  def __determine_exe(clazz, env_var_name, default_exe):
    return os.environ.get(env_var_name, default_exe)
  
  @classmethod
  def _run_perl_test(clazz, config, test_source):
    return clazz._run_exe_test('PERL', 'perl', config, test_source)

  _test_context = namedtuple('_test_context','package_info,env,saved_env,test_dir,test_name,test_source_with_replacements,package_manager')

  @classmethod
  def _make_test_context(clazz, config, test_source):
    test_name = path.splitext(path.basename(test_source))[0]
    test_root_dir = path.join(config.script.test_dir, test_name)
    pm_root_dir = path.join(test_root_dir, 'requirements')

    pm = package_manager(pm_root_dir)

    package = pm.load_tarball(config.package_tarball, config.script.build_target, config.artifact_manager)
    pd = package.info
    
    deps_packages = pd.resolved_requirements + pd.resolved_build_requirements
    all_packages = deps_packages + [ pd ]

    pm.install_packages(deps_packages, config.script.build_target, config.artifact_manager)
    pm.install_tarball(config.package_tarball)

    config.tools_manager.update(pd.resolved_build_tool_requirements, config.artifact_manager)

    saved_env = os_env.clone_current_env()

    config.tools_manager.export_variables_to_current_env(pd.resolved_build_tool_requirements)
    pm.export_variables_to_current_env(all_packages)

    shell_env = os_env.make_clean_env()
    os_env.update(shell_env, config.tools_manager.shell_env(pd.resolved_build_tool_requirements), prepend = True)
    os_env.update(shell_env, pm.shell_env(all_packages), prepend = True)
    
    test_source_with_replacements = path.join(test_root_dir, path.basename(test_source))
    replacements = {
      'REBUILDER_SOURCE_DIR': config.script.source_dir,
      'REBUILDER_TEST_DIR': config.script.test_dir,
      'REBUILDER_TEST_NAME': test_name,
    }
    substitutions = {}
    substitutions['REBUILDER_BUILD_DIR'] = config.script.build_dir
    for kv in config.extra_env:
      shell_env[kv.key] = variable.substitute(kv.value, substitutions)
      
    file_replace.copy_with_substitute(test_source, test_source_with_replacements,
                                      replacements, backup = False)
    return clazz._test_context(package.info, shell_env, saved_env,
                               test_root_dir, test_name,
                               test_source_with_replacements,
                               pm)

  @classmethod
  def _run_exe_test(clazz, exe_env_name, exe_default, config, test_source):
    context = clazz._make_test_context(config, test_source)
    build_blurb.blurb_verbose('tester', '%s: running shell test %s' % (context.package_info.name, test_source))
    exe = clazz.__determine_exe(exe_env_name, exe_default)
    cmd = '%s %s' % (exe, context.test_source_with_replacements)
    rv = execute.execute(cmd, env = context.env, non_blocking = build_blurb.verbose,
                         stderr_to_stdout = True, raise_error = False)
    os.environ = context.saved_env
    if rv.exit_code != 0:
      return step_result(rv.exit_code == 0, rv.stdout)
    return step_result(True, None)

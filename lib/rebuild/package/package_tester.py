#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from collections import namedtuple

from rebuild.step import step_result
from rebuild.base import build_blurb, build_target
from rebuild.toolchain import toolchain
from bes.dependency import dependency_resolver
from bes.common import algorithm, variable
from bes.system import execute, os_env
from bes.fs import file_replace
from bes.debug import debug_timer

from .package import package
from .package_manager import package_manager

class package_tester(object):

  test_config = namedtuple('test_config', 'script, package_tarball, artifact_manager, tools_manager, extra_env')

  def __init__(self, config, test):
    self._config = config
    self._test = test

  def run(self):
    rv = self._run_test(self._config, self._test)
    return rv

  @classmethod
  def _run_test(clazz, config, test):
    build_blurb.blurb('tester', 'Testing %s with %s' % (path.relpath(config.package_tarball), path.relpath(test)))
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
      raise RuntimeError('Uknown test type for %s: %s - %s' % (config.script.descriptor.full_name, str(test), type(test)))

  @classmethod
  def _run_c_test(clazz, config, test_source, compiler, extra_cflags):
    context = clazz._make_test_context(config, test_source)
    build_blurb.blurb_verbose('tester', '%s: running c test %s with %s' % (context.package_info.name, path.relpath(test_source), compiler))
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
  def _determine_exe(clazz, env_var_name, default_exe):
    return os.environ.get(env_var_name, default_exe)
  
  @classmethod
  def _run_perl_test(clazz, config, test_source):
    return clazz._run_exe_test('PERL', 'perl', config, test_source)

  _test_context = namedtuple('_test_context', 'package_info, env, saved_env, test_dir, test_name, test_source_with_replacements, package_manager')

  @classmethod
  def _make_test_context(clazz, config, test_source):
    timer = debug_timer('am', 'error', disabled = True)
    timer.start('_make_test_context()')
    test_name = path.splitext(path.basename(test_source))[0]
    test_root_dir = path.join(config.script.test_dir, test_name)
    pm_root_dir = path.join(test_root_dir, 'requirements')

    pm = package_manager(pm_root_dir, config.artifact_manager)

    timer.start('load tarball')
    package = pm.load_tarball(config.package_tarball, config.script.build_target)
    timer.stop()
    pd = package.package_descriptor
    
    timer.start('resolve_deps')
    deps_packages = config.script.resolve_deps(['RUN', 'TEST'], False)
    timer.stop()
    all_packages = deps_packages + [ pd ]
    all_packages_names = [ p.name for p in all_packages ]

    timer.start('install packages')
    pm.install_packages(deps_packages, config.script.build_target, ['RUN', 'TEST'])
    timer.stop()
    timer.start('install tarball')
    pm.install_tarball(config.package_tarball, package.metadata, ['RUN', 'TEST'])
    timer.stop()

    tool_reqs = pd.requirements.filter_by(['TOOL'], config.script.env.config.host_build_target.system)
    tool_reqs_names = tool_reqs.names()
    timer.start('resolve tools deps')
    resolved_tool_reqs = config.artifact_manager.resolve_deps(tool_reqs_names,
                                                              config.script.env.config.host_build_target,
                                                              [ 'TOOL' ],
                                                              True)
    timer.stop()
    timer.start('tools update')
    config.tools_manager.ensure_tools(resolved_tool_reqs)
    timer.stop()

    saved_env = os_env.clone_current_env()

    shell_env = os_env.make_clean_env()
    shell_env = config.tools_manager.transform_env(shell_env, resolved_tool_reqs)
    shell_env = pm.transform_env(shell_env, all_packages_names)
    
    test_source_with_replacements = path.join(test_root_dir, path.basename(test_source))
    substitutions = {}
    substitutions.update(config.script.substitutions)
    substitutions.update({ 
      'REBUILD_TEST_NAME': test_name,
      'REBUILD_SHELL_FRAMEWORK_DIR': pm.shell_framework_dir,
      '_REBUILD_DEV_ROOT': pm.shell_framework_dir,
    })
    for key, value in config.extra_env.items():
      shell_env[key] = variable.substitute(value, substitutions, patterns = variable.BRACKET)
    shell_env.update(substitutions)
    file_replace.copy_with_substitute(test_source, test_source_with_replacements,
                                      substitutions, backup = False)
    timer.stop()
    return clazz._test_context(package.package_descriptor,
                               shell_env,
                               saved_env,
                               test_root_dir,
                               test_name,
                               test_source_with_replacements,
                               pm)

  @classmethod
  def _run_exe_test(clazz, exe_env_name, exe_default, config, test_source):
    context = clazz._make_test_context(config, test_source)
    build_blurb.blurb_verbose('tester', '%s: running shell test %s' % (context.package_info.name, test_source))
    exe = clazz._determine_exe(exe_env_name, exe_default)
    cmd = '%s %s' % (exe, context.test_source_with_replacements)
    rv = execute.execute(cmd, env = context.env, non_blocking = build_blurb.verbose,
                         stderr_to_stdout = True, raise_error = False)
    os.environ = context.saved_env
    if rv.exit_code != 0:
      return step_result(rv.exit_code == 0, rv.stdout)
    return step_result(True, None)

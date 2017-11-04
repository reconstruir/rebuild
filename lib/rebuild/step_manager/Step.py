#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# FIXME: unify the replacements here with those in step_pkg_config_make_pc.py

import copy, os, os.path as path

from abc import abstractmethod, ABCMeta
from collections import namedtuple
from bes.common import dict_util, object_util, string_util, Shell, variable
from bes.system import log
from bes.system.compat import with_metaclass
from rebuild.base import build_blurb, build_os_env, build_target, masked_config
from rebuild.toolchain import toolchain
from rebuild import hook, variable_manager
from rebuild.pkg_config import pkg_config
from bes.fs import file_util
from .step_result import step_result
from rebuild.hook_extra_code import HOOK_EXTRA_CODE
from .step_registry import step_register

class Step(with_metaclass(step_register, object)): #), with_metaclass(ABCMeta, object)):

  #@abstractmethod
  def execute(self, script, env, args):
    'Execute the step.'
    assert False
    return step_result(False, 'not implemented')
 
  def on_tag_changed(self):
    'Called when the tag changes.'
    pass
  
  def __init__(self):
    self._args = copy.deepcopy(getattr(self, '__step_global_args__', {}))
#    self.log_d('%s: Step.__init__() args=%s' % (self, self._args))
    
  @classmethod
  def parse_step_args(clazz, script, env, args):
    result = copy.deepcopy(clazz.global_args())
#    self.log_d('%s: Step.parse_step_args() global_args=%s' % (clazz, result))
    if args:
      assert isinstance(args, dict)
      result.update(args)
#    self.log_d('%s: Step.parse_step_args() result=%s' % (clazz, result))
    return result

  @classmethod
  def global_args(clazz):
    return getattr(clazz, '__step_global_args__', {})

  def sources_keys(self):
    return []

  def update_args(self, args):
    dict_util.update(self.args, args)

  @property
  def tag(self):
    return self.bes_log_tag__

  @tag.setter
  def tag(self, tag):
    log.add_logging(self, tag)
    build_blurb.add_blurb(self, tag)
    self.on_tag_changed()

  @property
  def args(self):
    return self._args

  @args.setter
  def args(self, args):
    if not isinstance(args, dict):
      raise RuntimeError('args needs to be a dict')
    self._args = args

  ENV_VARS = [
    'HOME',
    'LANG',
    'SHELL',
    'TERM',
    'TERM_PROGRAM',
    'TMOUT',
    'TMPDIR',
    'USER',
    '__CF_USER_TEXT_ENCODING',
   ]

  @classmethod
  def create_command_env(clazz, script):
    env = build_os_env.make_clean_env()

    STATIC = True
    assert script.descriptor.resolved_requirements != None
    export_compilation_flags_requirements = script.descriptor.export_compilation_flags_requirements(script.env.config.build_target.system)
    if STATIC:
      env['REBBE_PKG_CONFIG_STATIC'] = '1'
      
    if export_compilation_flags_requirements:
      cflags, libs = script.requirements_manager.compilation_flags(export_compilation_flags_requirements, static = STATIC)
    else:
      cflags = []
      libs = []

    cflags += script.descriptor.extra_cflags(script.env.config.build_target.system)

    env['REBUILD_REQUIREMENTS_CFLAGS'] = ' '.join(cflags)
    env['REBUILD_REQUIREMENTS_CXXFLAGS'] = ' '.join(cflags)
    env['REBUILD_REQUIREMENTS_LDFLAGS'] = ' '.join(libs)

    env['REBUILD_REQUIREMENTS_DIR'] = script.requirements_manager.installation_dir
    env['REBUILD_REQUIREMENTS_BIN_DIR'] = script.requirements_manager.bin_dir
    env['REBUILD_REQUIREMENTS_INCLUDE_DIR'] = script.requirements_manager.include_dir
    env['REBUILD_REQUIREMENTS_LIB_DIR'] = script.requirements_manager.lib_dir
    env['REBUILD_REQUIREMENTS_SHARE_DIR'] = script.requirements_manager.share_dir

    env['REBUILD_PACKAGER_BUILD_DIR'] = script.build_dir
    env['REBUILD_PACKAGER_SOURCE_DIR'] = script.source_dir
    env['REBUILD_PACKAGER_TEST_DIR'] = script.test_dir

    env['REBUILD_STAGE_PREFIX_DIR'] = script.stage_dir
    env['REBUILD_STAGE_PYTHON_LIB_DIR'] = path.join(script.stage_dir, 'lib/python')
    env['REBUILD_STAGE_FRAMEWORKS_DIR'] = path.join(script.stage_dir, 'frameworks')

    build_os_env.update(env, script.env.tools_manager.shell_env(script.descriptor.resolved_build_requirements))
    build_os_env.update(env, script.requirements_manager.shell_env(script.descriptor.resolved_requirements))
    build_os_env.update(env, build_os_env.make_shell_env(script.stage_dir))

    env['REBUILD_PYTHON_VERSION'] = '2.7'
    env['PYTHON'] = 'python%s' % (env['REBUILD_PYTHON_VERSION'])
    env['REBUILD_PYTHON_PLATFORM_NAME'] =  script.env.config.build_target.system

    env['REBUILD_PACKAGE_NAME'] = script.descriptor.name
    env['REBUILD_PACKAGE_DESCRIPTION'] = script.descriptor.name
    env['REBUILD_PACKAGE_VERSION'] = str(script.descriptor.version)

    tc = toolchain.get_toolchain(script.env.config.build_target)
    compiler_flags = tc.compiler_flags()
    env['REBUILD_COMPILE_CFLAGS'] = ' '.join(compiler_flags.get('CFLAGS', []))
    env['REBUILD_COMPILE_LDFLAGS'] = ' '.join(compiler_flags.get('LDFLAGS', []))
    env['REBUILD_COMPILE_CXXFLAGS'] = ' '.join(compiler_flags.get('CXXFLAGS', []))
    env['REBUILD_COMPILE_ARCH_FLAGS'] = ' '.join(compiler_flags.get('REBUILD_COMPILE_ARCH_FLAGS', []))
    env['REBUILD_COMPILE_OPT_FLAGS'] = ' '.join(compiler_flags.get('REBUILD_COMPILE_OPT_FLAGS', []))

    ce = tc.compiler_environment()
    build_os_env.update(env, ce)
    env['REBUILD_COMPILE_ENVIRONMENT'] = toolchain.flatten_for_shell(ce)

    env.update(variable_manager.get_variables())
      
    return env

  @classmethod
  def env_dump(clazz, env, package_name, label):
    for key, value in sorted(env.items()):
      build_blurb.blurb_verbose('build', '%s(%s): %s=%s' % (label, package_name, key, value))
  
  @classmethod
  def call_shell(clazz, command, script, env, args, extra_env = None, save_logs = None, execution_dir = None):
    command = Shell.listify_command(command)
    command = [ part for part in command if part ]
    extra_env = extra_env or {}
    save_logs = save_logs or []
    assert isinstance(extra_env, dict)
    log.log_i('build', 'call_shell(cmd=%s, args=%s)' % (command, args))
    build_blurb.blurb_verbose('build', 'call_shell(cmd=%s, args=%s, extra_env=%s)' % (command, args, extra_env))

    env = clazz.create_command_env(script)

    env.update(extra_env)

    clazz.env_dump(env, script.descriptor.name, 'PRE ENVIRONMENT')

    build_os_env.env_substitite(env)

    rogue_key = build_os_env.env_find_roque_dollar_sign(env)
    if rogue_key:
      raise RuntimeError('Rogue dollar sign (\"$\") found in %s: %s' % (rogue_key, env[rogue_key]))

    command = [ variable.substitute(part, env) for part in object_util.listify(command) ]

    # Check that no rogue dollar signs are in the command
    for part in command:
      if variable.has_rogue_dollar_signs(part):
        raise RuntimeError('Rogue dollar sign (\"$\") found in: %s' % (part))
      
    build_blurb.blurb('build', '%s - %s' % (script.descriptor.name, ' '.join(command)))

#    file_util.mkdir(script.build_dir)
    retry_script = clazz._write_retry_script(command, env, script)

    clazz.env_dump(env, script.descriptor.name, clazz.__name__ + ' : ' + 'POST ENVIRONMENT')

    for k,v in env.items():
      if string_util.is_quoted(v):
        env[k] = string_util.unquote(v)

    if execution_dir:
      cwd = path.join(script.build_dir, execution_dir)
    else:
      cwd = script.build_dir
    rv = Shell.execute(command,
                       cwd = cwd,
                       env = env,
                       shell = True,
                       non_blocking = build_blurb.verbose,
                       stderr_to_stdout = build_blurb.verbose,
                       raise_error = False)
    message = rv.stdout
    if rv.stderr:
      message = message + '\n' + rv.stderr
    result = step_result(rv.exit_code == 0, message)
    clazz.save_build_dir_logs(script, save_logs)
    return result

  RETRY_SCRIPT_FILENAME = 'rebbe_retry.sh'

  @classmethod
  def _write_retry_script(clazz, command, env, script):
    from bes.compat import StringIO
    s = StringIO()
    s.write('#!/bin/bash\n')
    s.write('mkdir -p %s\n' % (script.stage_dir))
    items = sorted(env.items())
    last_item = items.pop(-1)

    def _item_str(key, value, slash):
      return '%s=\"%s\"%s\n' % (key, value, slash)

    for key, value in items:
      s.write(_item_str(key, value, '\\'))

    s.write(_item_str(last_item[0], last_item[1], ''))

    if string_util.is_string(command):
      s.write(command)
    else:
      s.write(' '.join(command))
    content = s.getvalue()
    file_path = path.join(script.build_dir, clazz.RETRY_SCRIPT_FILENAME)
    file_util.save(file_path, content = content, mode = 0o755)
    return file_path

  @classmethod
  def resolve_step_args_list(clazz, script, args, name):
    if not name or not name in args:
      return {}
    config = args[name]
    resolved = masked_config.resolve_list(config, script.env.config.build_target.system)
    return { name: resolved }
      
  @classmethod
  def resolve_step_args_hooks(clazz, script, args, name):
    d = clazz.resolve_step_args_list(script, args, name)
    hooks = hook.parse_list(d.get(name, []))
    for h in hooks:
      h.root_dir = script.source_dir
    return { name: hooks }
  
  @classmethod
  def resolve_step_args_files(clazz, script, args, name):
    d = clazz.resolve_step_args_list(script, args, name)
    filenames = d.get(name, [])
    files = [ path.join(script.source_dir, f) for f in filenames ]
    for f in files:
      if not path.isfile(f):
        raise RuntimeError('Not found for \"%s\": %s' % (name, f))
    return { name: files }
  
  @classmethod
  def resolve_step_args_dir(clazz, script, args, name):
    if not name in args:
      return {}
    d = args.get(name, None)
    if not d:
      return {}
    if path.isdir(d):
      d = path.abspath(d)
    else:
      d = path.join(script.source_dir, d)
    if not path.isdir(d):
      raise RuntimeError('Dir not found for \"%s\": %s' % (name, d))
    return { name: d }

  @classmethod
  def resolve_step_args_env_and_flags(clazz, script, args, env_name, flags_name):
    assert env_name or flags_name

    env_dict = {}
    if env_name and env_name in args:
      config = args[env_name]
      resolved = masked_config.resolve_key_values_to_dict(config, script.env.config.build_target.system)
      assert isinstance(resolved, dict)
      env_dict = { env_name: resolved }

    flags_dict = {}
    if flags_name and flags_name in args:
      config = args[flags_name]
      resolved = masked_config.resolve_list(config, script.env.config.build_target.system)
      flags_dict = { flags_name: resolved }

    return dict_util.combine(env_dict, flags_dict)
  
  @classmethod
  def call_hooks(clazz, script, env, args, name):
    hooks = args.get(name, [])
    if not hooks:
      return step_result(True, None)
    for h in hooks:
      hook_result = h.execute(script, env, args, extra_code = HOOK_EXTRA_CODE)
      if not isinstance(hook_result, step_result):
        raise RuntimeError('hook did not return step_result: %s' % (h))
      if not hook_result.success:
        return hook_result
    return step_result(True, None)

  @classmethod
  def save_build_dir_logs(clazz, env, filenames):
    'Save any logs that exists to the logs/ dir'
    for filename in filenames:
      src = path.join(env.build_dir, filename)
      dst = path.join(env.logs_dir, path.basename(src))
      if path.isfile(src):
        file_util.copy(src, dst)

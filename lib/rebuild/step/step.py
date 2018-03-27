#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, os.path as path

from abc import abstractmethod, ABCMeta
from collections import namedtuple

from bes.common import check, dict_util, object_util, string_util, variable
from bes.fs import file_util
from bes.key_value import key_value_list
from bes.system import os_env, execute, log
from bes.system.compat import with_metaclass
from bes.text import string_list
from rebuild.base import build_blurb, build_target, reitred_masked_config
from bes.dependency import dependency_resolver
from rebuild.toolchain import toolchain
from rebuild.value import value_type

from .hook_poto import hook_poto
from .hook_extra_code import HOOK_EXTRA_CODE
from .step_registry import step_registry
from .step_result import step_result
from .variable_manager import variable_manager
from .step_arg_spec import step_arg_spec

class step_register_meta(ABCMeta, value_type.CONSTANTS):

  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    step_registry.register_step_class(clazz)
#    clazz._determine_args_definition()
    return clazz

class step(with_metaclass(step_register_meta, object)):

  def __init__(self):
    self._recipe = None
    self._args = copy.deepcopy(getattr(self, '__step_global_args__', {}))
#    self.log_d('%s: step.__init__() args=%s' % (self, self._args))

  @classmethod
  def args_definition(clazz):
    if not hasattr(clazz, '_args_definition'):
      setattr(clazz, '_args_definition', clazz._determine_args_definition())
    return getattr(clazz, '_args_definition')

  @classmethod
  def _determine_args_definition(clazz):
    defs = clazz.define_args()
    if check.is_string(defs):
      defs = step_arg_spec.parse_many(defs)
    check.check_dict(defs)
    return defs

#  @abstractmethod
  def prepare(self, script, env, args):
    'Prepare the step.'
    pass
 
  @abstractmethod
  def execute(self, script, env, args):
    'Execute the step.'
    pass
 
  def sources(self):
    'Return a list of sources for this step.'
    return []
 
  def on_tag_changed(self):
    'Called when the tag changes.'
    pass

  @classmethod
#  @abstractmethod
  def define_args(clazz):
    'Return a list of arg specs.'
    return {}
  
  @classmethod
  def parse_step_args(clazz, script, env, args):
    result = copy.deepcopy(clazz.global_args())
#    self.log_d('%s: step.parse_step_args() global_args=%s' % (clazz, result))
    if args:
      assert isinstance(args, dict)
      result.update(args)
#    self.log_d('%s: step.parse_step_args() result=%s' % (clazz, result))
    return result

  @classmethod
  def global_args(clazz):
    return getattr(clazz, '__step_global_args__', {})

  def sources_keys(self):
    return []

  def update_args(self, args):
    dict_util.update(self.args, args)

  @property
  def recipe(self):
    assert self._recipe != None
    return self._recipe

  @recipe.setter
  def recipe(self, recipe):
    assert recipe != None
    assert self._recipe == None
    self._recipe = recipe

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
    #env = os_env.make_clean_env()
    env = os_env.make_clean_env(keep_keys = [ 'PYTHONPATH' ])

    STATIC = True
    export_compilation_flags_requirements = clazz.export_compilation_flags_requirements(script, script.build_target.system)
    if STATIC:
      env['REBBE_PKG_CONFIG_STATIC'] = '1'
      
    if export_compilation_flags_requirements:
      cflags, libs = script.requirements_manager.compilation_flags(export_compilation_flags_requirements, static = STATIC)
    else:
      cflags = []
      libs = []

    cflags += script.descriptor.extra_cflags(script.build_target.system)

    env['REBUILD_REQUIREMENTS_CFLAGS'] = ' '.join(cflags)
    env['REBUILD_REQUIREMENTS_CXXFLAGS'] = ' '.join(cflags)
    env['REBUILD_REQUIREMENTS_LDFLAGS'] = ' '.join(libs)

    env['REBUILD_REQUIREMENTS_DIR'] = script.requirements_manager.installation_dir
    env['REBUILD_REQUIREMENTS_BIN_DIR'] = script.requirements_manager.bin_dir
    env['REBUILD_REQUIREMENTS_INCLUDE_DIR'] = script.requirements_manager.include_dir
    env['REBUILD_REQUIREMENTS_LIB_DIR'] = script.requirements_manager.lib_dir
    env['REBUILD_REQUIREMENTS_SHARE_DIR'] = script.requirements_manager.share_dir

    env['REBUILD_BUILD_DIR'] = script.build_dir
    env['REBUILD_SOURCE_DIR'] = script.source_dir
    env['REBUILD_TEST_DIR'] = script.test_dir

    env['REBUILD_STAGE_PREFIX_DIR'] = script.stage_dir
    env['REBUILD_STAGE_BIN_DIR'] = path.join(script.stage_dir, 'bin')
    env['REBUILD_STAGE_PYTHON_LIB_DIR'] = path.join(script.stage_dir, 'lib/python')
    env['REBUILD_STAGE_FRAMEWORKS_DIR'] = path.join(script.stage_dir, 'frameworks')

    os_env.update(env, script.env.tools_manager.shell_env(script.resolve_deps_caca_tool(False)))
    os_env.update(env, script.requirements_manager.shell_env(script.resolve_deps_poto_run(False)))
    os_env.update(env, os_env.make_shell_env(script.stage_dir))

    env['REBUILD_PYTHON_VERSION'] = '2.7'
    env['PYTHON'] = 'python%s' % (env['REBUILD_PYTHON_VERSION'])
    env['REBUILD_PYTHON_PLATFORM_NAME'] =  script.build_target.system

    env['REBUILD_PACKAGE_NAME'] = script.descriptor.name
    env['REBUILD_PACKAGE_DESCRIPTION'] = script.descriptor.name
    env['REBUILD_PACKAGE_VERSION'] = str(script.descriptor.version)

    tc = toolchain.get_toolchain(script.build_target)
    compiler_flags = tc.compiler_flags()
    env['REBUILD_COMPILE_CFLAGS'] = ' '.join(compiler_flags.get('CFLAGS', []))
    env['REBUILD_COMPILE_LDFLAGS'] = ' '.join(compiler_flags.get('LDFLAGS', []))
    env['REBUILD_COMPILE_CXXFLAGS'] = ' '.join(compiler_flags.get('CXXFLAGS', []))
    env['REBUILD_COMPILE_ARCH_FLAGS'] = ' '.join(compiler_flags.get('REBUILD_COMPILE_ARCH_FLAGS', []))
    env['REBUILD_COMPILE_OPT_FLAGS'] = ' '.join(compiler_flags.get('REBUILD_COMPILE_OPT_FLAGS', []))

    ce = tc.compiler_environment()
    os_env.update(env, ce)
    env['REBUILD_COMPILE_ENVIRONMENT'] = toolchain.flatten_for_shell(ce)

    env.update(variable_manager.get_variables())
      
    return env

  @classmethod
  def env_dump(clazz, env, package_name, label):
    for key, value in sorted(env.items()):
      build_blurb.blurb_verbose('build', '%s(%s): %s=%s' % (label, package_name, key, value))
  
  @classmethod
  def call_shell(clazz, command, script, env, args, extra_env = None, save_logs = None, execution_dir = None):
    command = execute.listify_command(command)
    command = [ part for part in command if part ]
    extra_env = extra_env or key_value_list()
    save_logs = save_logs or []
    check.check_key_value_list(extra_env)
    
    log.log_i('build', 'call_shell(cmd=%s, args=%s)' % (command, args))
    build_blurb.blurb_verbose('build', 'call_shell(cmd=%s, args=%s, extra_env=%s)' % (command, args, extra_env))

    env = clazz.create_command_env(script)

    env.update(extra_env)

    clazz.env_dump(env, script.descriptor.name, 'PRE ENVIRONMENT')

    clazz._env_substitite(env)

    rogue_key = clazz._env_find_roque_dollar_sign(env)
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

    rv = execute.execute(command,
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
    resolved = reitred_masked_config.resolve_list(config, script.build_target.system)
    return { name: resolved }
      
  @classmethod
  def resolve_step_args_files(clazz, script, args, name):
    d = clazz.resolve_step_args_list(script, args, name)
    filenames = d.get(name, [])
    files = [ path.join(script.source_dir, f) for f in filenames ]
    import os
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
      resolved = reitred_masked_config.resolve_key_values(config, script.build_target.system)
      check.check_key_value_list(resolved)
      env_dict = { env_name: resolved }

    flags_dict = {}
    if flags_name and flags_name in args:
      config = args[flags_name]
      resolved = reitred_masked_config.resolve_list(config, script.build_target.system)
      check.check_list(resolved)
      flags_dict = { flags_name: resolved }

    return dict_util.combine(env_dict, flags_dict)
  
  @classmethod
  def resolve_step_args_key_values(clazz, script, args, key):
    result = {}
    if key and key in args:
      config = args[key]
      resolved = reitred_masked_config.resolve_key_values(config, script.build_target.system)
      check.check_key_value_list(resolved)
      result = { key: resolved }
    return result

  @classmethod
  def resolve_step_args_hooks(clazz, script, args, name):
    d = clazz.resolve_step_args_list(script, args, name)
    hooks = hook_poto.parse_list(d.get(name, []))
    for h in hooks:
      h.root_dir = script.source_dir
    return { name: hooks }
  
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

  @classmethod
  def export_compilation_flags_requirements(clazz, script, system):
    config = script.descriptor.properties.get('export_compilation_flags_requirements', [])
    resolved = reitred_masked_config.resolve_list(config, system)
    requirements = script.descriptor.requirements.filter_by_hardness(['RUN', 'BUILD']).filter_by_system(system)
    deps_names = requirements.names()
    export_names = resolved
    if export_names == dependency_resolver.ALL_DEPS:
      export_names = deps_names
    delta = (set(export_names) - set(deps_names))
    if delta:
      raise RuntimeError('Trying to export deps that are not specified by %s: %s' % (script.descriptor.name, ' '.join(delta)))
    return export_names
        
  @classmethod
  def args_get_string_list(clazz, args, key):
    check.check_dict(args)
    result = args.get(key, string_list())
    if not result:
      return string_list()
    if check.is_string_seq(result):
      result = string_list(result)
    check.check_string_list(result)
    return result

  @classmethod
  def args_get_key_value_list(clazz, args, key):
    check.check_dict(args)
    result = args.get(key, None) or key_value_list()
    check.check_key_value_list(result)
    return result

  @classmethod
  def _env_find_roque_dollar_sign(clazz, env):
    for key in sorted(env.keys()):
      if variable.has_rogue_dollar_signs(env[key]):
        return key
    return None

  @classmethod
  def _env_substitite(clazz, env):
    for key in sorted(env.keys()):
      env[key] = variable.substitute(str(env[key]), env)

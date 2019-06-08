#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, inspect, os, os.path as path, sys

from abc import abstractmethod, ABCMeta
from collections import namedtuple

from bes.common.check import check
from bes.common.dict_util import dict_util
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.common.variable import variable
from bes.common.variable_pattern import variable_pattern
from bes.dependency.dependency_resolver import dependency_resolver
from bes.factory.singleton_class_registry import singleton_class_registry
from bes.fs.file_util import file_util
from bes.key_value.key_value_list import key_value_list
from bes.system.os_env import os_env
from bes.system.execute import execute
from bes.system.log import log
from bes.system.compat import with_metaclass

from rebuild.base.build_blurb import build_blurb
from rebuild.base.build_target import build_target
from rebuild.recipe.value.value_definition import value_definition
from rebuild.recipe.value.value_type import value_type
from rebuild.toolchain.toolchain import toolchain

from .step_registry import step_registry
from .step_result import step_result

class step_register_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    step_registry.register(clazz)
    return clazz

class step(with_metaclass(step_register_meta, object)):

  result = step_result
  
  def __init__(self):
    log.add_logging(self, tag = 'step')
    build_blurb.add_blurb(self, 'rebuild')
    self._recipe = None
    self._args = {}
    self._values = None
    
  @property
  def values(self):
    if self._values is None:
      raise ValueError('values have not been set yet.')
    return self._values

  @values.setter
  def values(self, values):
    check.check_dict(values)
    if self._values is not None:
      raise ValueError('values can only be set once.')
    self._values = values
  
  @classmethod
  def args_definition(clazz):
    if not hasattr(clazz, '_args_definition'):
      setattr(clazz, '_args_definition', clazz._determine_args_definition())
    return getattr(clazz, '_args_definition')

  @classmethod
  def _determine_args_definition(clazz):
    defs = clazz.define_args()
    if check.is_string(defs):
      try:
        defs = value_definition.parse_many(defs)
      except RuntimeError as ex:
        filename = inspect.getfile(clazz.define_args)
        line_number = inspect.getsourcelines(clazz.define_args)[1]
        raise RuntimeError('%s: %s:%s' % (ex.message, filename, line_number))
      check.check_dict(defs)
    return defs

  @abstractmethod
  def execute(self, script, env, values, inputs):
    'Execute the step.'
    pass
 
  @classmethod
  @abstractmethod
  def define_args(clazz):
    'Return a list of arg specs.'
    return {}
  
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
  def args(self):
    return self._args

  @args.setter
  def args(self, args):
    if not isinstance(args, dict):
      raise RuntimeError('args needs to be a dict')
    self._args = args

  @classmethod
  def create_command_env(clazz, script):
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

    env.update(script.substitutions)
    env.update(script.env.variable_manager.variables)
    tool_deps = script.resolve_deps(['TOOL'], False)
    run_build_deps = script.resolve_deps(['RUN', 'BUILD'], False)
    env = script.env.tools_manager.transform_env(env, tool_deps)
    env = script.requirements_manager.transform_env(env, run_build_deps.names())
    staged_files_env = os_env.make_shell_env(script.staged_files_dir)
    os_env.update(env, staged_files_env)
    
    env['REBUILD_PYTHON_VERSION'] = '2.7'
    env['PYTHON'] = 'python%s' % (env['REBUILD_PYTHON_VERSION'])
    
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

    return env

  @classmethod
  def env_dump(clazz, env, package_name, label):
    for key, value in sorted(env.items()):
      build_blurb.blurb_verbose('rebuild', '%s(%s): %s=%s - %s' % (label, package_name, key, value, type(value)))
  
  @classmethod
  def call_shell(clazz, command, script, env, shell_env = None, save_logs = None, execution_dir = None):
    command = execute.listify_command(command)
    command = [ part for part in command if part ]
    shell_env = shell_env or key_value_list()
    save_logs = save_logs or []
    check.check_key_value_list(shell_env)
    
    log.log_i('rebuild', 'call_shell(command=%s)' % (command))
    build_blurb.blurb_verbose('rebuild', 'call_shell(cmd=%s, shell_env=%s)' % (command, shell_env))

    env = clazz.create_command_env(script)

    env.update(shell_env)

    #clazz.env_dump(env, script.descriptor.name, 'PRE ENVIRONMENT')

    #self.log_i('%s=%s - %s' % (key, env[key], type(env[key])))
    
    clazz._env_substitite(env)

    rogue_key = clazz._env_find_roque_dollar_sign(env)
    if rogue_key:
      raise RuntimeError('%s: Rogue dollar sign (\"$\") found in %s: %s' % (script.recipe.filename, rogue_key, env[rogue_key]))

    command = [ variable.substitute(part, env, patterns = variable_pattern.BRACKET) for part in object_util.listify(command) ]

    # Check that no rogue dollar signs are in the command
    for part in command:
      if variable.has_rogue_dollar_signs(part):
        raise RuntimeError('%s: Rogue dollar sign (\"$\") found in: %s' % (script.recipe.filename, part))
      
    build_blurb.blurb('rebuild', '%s - %s' % (script.descriptor.name, ' '.join(command)))

#    file_util.mkdir(script.build_dir)
    retry_script = clazz._write_retry_script(command, env, script)

    #clazz.env_dump(env, script.descriptor.name, clazz.__name__ + ' : ' + 'POST ENVIRONMENT')

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
    result = step_result(rv.exit_code == 0, message, stdout = rv.stdout)
    clazz.save_build_dir_logs(script, save_logs)
    return result

  RETRY_SCRIPT_FILENAME = 'rebbe_retry.sh'

  @classmethod
  def _write_retry_script(clazz, command, env, script):
    from bes.compat.StringIO import StringIO
    s = StringIO()
    s.write('#!/bin/bash\n')
    s.write('mkdir -p %s\n' % (script.staged_files_dir))
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
  def call_hooks(clazz, hooks, script, env):
    check.check_value_hook_list(hooks, allow_none = True)
    for hook in (hooks or []):
      build_blurb.blurb('rebuild', '%s: calling hook: %s' % (script.descriptor.name, str(hook)))
      rv = hook.execute(script, env)
      check.is_hook_result(rv)
      if not rv.success:
        return step_result(rv.success, rv.message)
    return step_result(True, None)
  
  @classmethod
  def call_hooks_inline(clazz, hooks, script, env):
    check.check_value_hook_list_inline(hooks)
    for hook in hooks:
      rv = hook.execute(script, env)
      check.is_hook_result(rv)
      if not rv.success:
        return step_result(rv.success, rv.message)
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
    if config:
      if check.is_masked_value_list(config):
        resolved = config.resolve(system, value_type.STRING_LIST)
      else:
        raise RuntimeError('not a valid masked_value_list: %s' % (config))
    else:
      resolved = []
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
  def _env_find_roque_dollar_sign(clazz, env):
    for key in sorted(env.keys()):
      if variable.has_rogue_dollar_signs(env[key]):
        return key
    return None

  @classmethod
  def _env_substitite(clazz, env):
    for key in sorted(env.keys()):
      env[key] = variable.substitute(str(env[key]), env, patterns = variable_pattern.BRACKET)
      
check.register_class(step, include_seq = False)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple

from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.json_util import json_util
from bes.common.string_util import string_util
from bes.common.type_checked_list import type_checked_list
from bes.common.variable import variable
from bes.debug.debug_timer import debug_timer
from bes.dependency import dependency_provider
from bes.fs.file_checksum import file_checksum_list
from bes.fs.file_util import file_util
from bes.system.log import log
from bes.system.python import python

from rebuild.base.build_blurb import build_blurb
from rebuild.package.package_manager import package_manager
from rebuild.recipe.recipe_data_manager import recipe_data_manager
from rebuild.recipe.value.value_file import value_file
from rebuild.step.step_description import step_description
from rebuild.step.step_manager import step_manager

class builder_script(object):

  # which version of python to use for all builder related subprocess calls
  _PYTHON_VERSION = '2.7'
  #_PYTHON_VERSION = '3.7'
  
  def __init__(self, recipe, build_target, env):
    log.add_logging(self, 'rebuild')
    build_blurb.add_blurb(self, 'rebuild')

    check.check_recipe(recipe)
    check.check_build_target(build_target)

    self.env = env
    self.timer = self.env.config.timer
    self.recipe = recipe
    self.build_target = build_target
    self.enabled = recipe.enabled.parse_expression(self.build_target)
    self.recipe_dir = path.dirname(self.filename)
    self._step_manager = step_manager('rebuild')
    self.working_dir = self._make_working_dir(self.env.config.builds_dir(self.build_target),
                                              self.descriptor.full_name,
                                              self.env.config.timestamp)
    self.source_unpacked_dir = path.join(self.working_dir, 'source')
    self.build_dir = path.join(self.working_dir, 'build')

    self.stage_dir = path.join(self.working_dir, 'stage')
    self.staged_files_dir = path.join(self.stage_dir, 'files')
    self.staged_files_lib_dir = path.join(self.staged_files_dir, 'lib')
    self.staged_files_bin_dir = path.join(self.staged_files_dir, 'bin')
    self.staged_files_instructions_dir = path.join(self.staged_files_lib_dir, 'rebuild_instructions')
    self.stagged_env_dir = path.join(self.stage_dir, 'env')

    self.artifact_dir = path.join(self.working_dir, 'artifact')
    self.logs_dir = path.join(self.working_dir, 'logs')
    self.test_dir = path.join(self.working_dir, 'test')
    self.check_dir = path.join(self.working_dir, 'check')
    self.temp_dir = path.join(self.working_dir, 'temp')
    self.python_lib_dir = path.join(self.staged_files_dir, 'lib/python')
    self.requirements_manager = package_manager(path.join(self.working_dir, 'requirements'),
                                                env.requirements_artifact_manager)
    self.recipe_data_manager = recipe_data_manager()
    self.recipe_data_manager.set_from_tuples(self.recipe.resolve_data(self.build_target.system))

    python_exe = 'python{}'.format(self._PYTHON_VERSION)
    self.substitutions = {
      'REBUILD_WORKING_DIR': self.working_dir,
      'REBUILD_BUILD_DIR': self.build_dir,
      'REBUILD_PACKAGE_DESCRIPTION':  self.descriptor.name,
      'REBUILD_PACKAGE_FULL_NAME':  self.descriptor.full_name,
      'REBUILD_PACKAGE_FULL_VERSION':  str(self.descriptor.version),
      'REBUILD_PACKAGE_NAME':  self.descriptor.name,
      'REBUILD_PACKAGE_UPSTREAM_VERSION':  self.descriptor.version.upstream_version,
      'REBUILD_PYTHON_PLATFORM_NAME':   self.build_target.system,
      'REBUILD_RECIPE_DIR': path.abspath(self.recipe_dir),
      'REBUILD_REQUIREMENTS_BIN_DIR': self.requirements_manager.bin_dir,
      'REBUILD_REQUIREMENTS_DIR': self.requirements_manager.installation_dir,
      'REBUILD_REQUIREMENTS_INCLUDE_DIR': self.requirements_manager.include_dir,
      'REBUILD_REQUIREMENTS_LIB_DIR': self.requirements_manager.lib_dir,
      'REBUILD_REQUIREMENTS_SHARE_DIR': self.requirements_manager.share_dir,
      'REBUILD_SOURCE_UNPACKED_DIR': self.source_unpacked_dir,
      'REBUILD_STAGE_FRAMEWORKS_DIR':  path.join(self.staged_files_dir, 'frameworks'),
      'REBUILD_STAGE_PREFIX_DIR':  self.staged_files_dir,
      'REBUILD_STAGE_PYTHON_LIB_DIR':  self.python_lib_dir,
      'REBUILD_STAGE_LIB_DIR':  self.staged_files_lib_dir,
      'REBUILD_STAGE_BIN_DIR':  self.staged_files_bin_dir,
      'REBUILD_TEMP_DIR': self.temp_dir,
      'REBUILD_TEST_DIR': self.test_dir,
      'REBUILD_PYTHON': python_exe,
      'REBUILD_PYTHON_VERSION': python.exe_version(python_exe),
    }
    for kv in self.recipe.resolve_variables(self.build_target.system):
      if kv.key in self.substitutions:
        raise ValueError('Cannot override system variables in recipe: %s' % (kv.key))
      self.substitutions[kv.key] = kv.value
    for key, value in self.env.variable_manager.variables.items():
      if key in self.substitutions:
        raise ValueError('Cannot override system variables in recipe: %s' % (key))
      self.substitutions[key] = value

    self._env_checksum_filename = path.join(self.env.config.build_root,
                                            'checksums',
                                            self.build_target.build_path,
                                            self.descriptor.full_name,
                                            'env.json')
    self._save_env_checksum_if_changed()
    self._add_steps()

  def substitute(self, d):
    'Substitute variables in dict d with self.substitutions.'
    return variable.substitute(d, self.substitutions, patterns = variable.BRACKET)
    
  def _save_env_checksum(self):
    content = self._env_checksum_content()
    file_util.save(self._env_checksum_filename, content = content)
    
  def _save_env_checksum_if_changed(self):
    if not path.isfile(self._env_checksum_filename):
      return
    content = self._env_checksum_content()
    if file_util.read(self._env_checksum_filename, codec = 'utf8') == content:
      return
    file_util.save(self._env_checksum_filename, content = content)
    
  def _env_checksum_content(self):
    vv = variable.find_variables(file_util.read(self.recipe.filename, codec = 'utf8'))
    d = copy.deepcopy(self.substitutions)
    for k, v in self.substitutions.items():
      if k not in vv or self.working_dir in v:
        del d[k]
    return json_util.to_json(d, indent = 2)
    
  def step_values_as_dict(self):
    return self._step_manager.step_values_as_dict()
  
  @property
  def descriptor(self):
    return self.recipe.descriptor
    
  @property
  def filename(self):
    return self.recipe.filename
    
  @property
  def properties(self):
    return self.recipe.properties
  
  def resolve_deps(self, hardness, include_names):
    return self.env.resolve_deps(self.descriptor, hardness, include_names)
  
  @property
  def instructions(self):
    return self.recipe.instructions
    
  @property
  def steps(self):
    return self.recipe.steps

  @classmethod
  def _make_working_dir(clazz, build_dir, full_name, timestamp):
    base_dir = '%s_%s' % (full_name, timestamp)
    return path.join(build_dir, base_dir)
    
  def _add_steps(self):
    if not self.enabled:
      return
    try:
      self._step_manager.add_steps(self.steps, self, self.env)
    except Exception as ex:
      print(('Caught exception adding steps to script: %s' % (self.filename)))
      raise

  def execute(self):
    result = self._step_manager.execute(self, self.env)
    if result.success:
      if not self.env.config.is_partial_build:
        self._save_env_checksum()
        self.env.checksum_manager.save_checksums(self._current_checksums(self.env.script_manager.scripts),
                                                 self.descriptor,
                                                 self.build_target)
    return result

  file_checksums = namedtuple('file_checksums', 'sources, targets')

  def _script_sources(self):
    sources = self._step_manager.sources(self.env.recipe_load_env, self.substitutions)
    sources.append(self.filename)
    sources = [ self._path_normalize(s) for s in sources if s ]
    return sorted(sources)

  @classmethod
  def _path_normalize(clazz, p):
    if path.isabs(p):
      result = path.relpath(p)
      if result.startswith(path.pardir):
        return p
      else:
        return result
    else:
      return p
    
  def _dep_sources(self, all_scripts):
    'Return a list of dependency sources for this script.'
    if not all_scripts:
      print('WEIRD a build script with no all_scripts: %s' % (self.filename))
      return []
    sources = []
    for dep in self.resolve_deps(['BUILD', 'RUN'], False):
      dep_script = all_scripts[dep.name]
      sources += dep_script._sources(all_scripts)
    return sources

  def _sources(self, all_scripts):
    'Return a list of all script and dependency sources for this script.'
    sources = self._script_sources() + self._dep_sources(all_scripts)
    sources.append(path.relpath(self._env_checksum_filename))
    result = []
    for source in sources:
      s = variable.substitute(source, self.substitutions, patterns = variable.BRACKET)
      if path.isfile(s):
        result.append(s)
      else:
        pass #print('you suck so bad because file not found: %s' % (s))
    return algorithm.unique(result)

  def _targets(self):
    p = self.env.build_artifact_manager.artifact_path(self.descriptor, self.build_target, False)
    if not p:
      return []
    return [ self._path_normalize(p) ]

  def _current_checksums(self, all_scripts):
    return self.file_checksums(file_checksum_list.from_files(self._sources(all_scripts), getter = self.env.checksum_getter),
                               file_checksum_list.from_files(self._targets(), getter = self.env.checksum_getter))

  def needs_rebuilding(self):
    try:
      loaded_checksums = self.env.checksum_manager.load_checksums(self.descriptor,
                                                                  self.build_target)
      
      # If the stored checksums don't match the current checksums, then we need to rebuild
      if loaded_checksums:
        loaded_source_filenames = loaded_checksums.sources.filenames()
        loaded_target_filenames = loaded_checksums.targets.filenames()
        current_checksums = self._current_checksums(self.env.script_manager.scripts)
        current_source_filenames = current_checksums.sources.filenames()
        current_target_filenames = current_checksums.targets.filenames()
        if current_source_filenames != loaded_source_filenames:
          return True, 'sources list changed'

        if loaded_target_filenames != current_target_filenames:
          return True, 'target filenames changed'
          
      if not loaded_checksums:
        return True, 'checksums missing'
      verification = loaded_checksums.sources.verify(getter = self.env.checksum_getter)
      if not verification:
        return True, 'checksums changed'
      return False
    except IOError as ex:
      return True, 'error: %s' % (str(ex))

  def format_message(self, message):
    'Format a build message to be as pretty and compact as possible.'
    format_vars = {
      'staged_files_dir': self.staged_files_dir,
      'stage_dir': self.stage_dir,
    }
    formatted_message = message.format(**format_vars)
    replacemetns = {
      self.working_dir: self._shorten_path(self.working_dir),
    }
    return string_util.replace(formatted_message, replacemetns)

  def has_staged_files_dir(self):
    return path.isdir(self.staged_files_dir)
  
  def has_stage_dir(self):
    return path.isdir(self.stage_dir)

  @classmethod
  def _shorten_path(clazz, p):
    relp = path.relpath(p)
    if relp.startswith('..'):
      return p
    return relp

  def timer_start(self, thing):
    self.timer.start(thing)

  def timer_stop(self):
    self.timer.stop()

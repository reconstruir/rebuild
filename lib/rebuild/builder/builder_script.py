#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple

from bes.common import algorithm, check, variable
from bes.fs import file_checksum, file_util
from bes.system import log
from rebuild.base import build_blurb, build_target
from bes.dependency import dependency_provider
from rebuild.step import step_description, step_manager
from rebuild.package import package_manager

class builder_script(object):

  def __init__(self, recipe, env):
    log.add_logging(self, 'build')
    build_blurb.add_blurb(self, 'build')
    self.env = env
    self.recipe = recipe
    self.build_target = env.config.build_target
    self.enabled = self.build_target.parse_expression(recipe.enabled)
    self.source_dir = path.dirname(self.filename)
    self._step_manager = step_manager('build')
    self.working_dir = self._make_working_dir(self.env.config.builds_dir(self.build_target),
                                              self.descriptor.full_name,
                                              self.env.config.timestamp)
    self.source_unpacked_dir = path.join(self.working_dir, 'source')
    self.build_dir = path.join(self.working_dir, 'build')
    self.stage_dir = path.join(self.working_dir, 'stage')
    self.env_dir = path.join(self.working_dir, 'env')
    self.artifact_stage_dir = path.join(self.working_dir, 'artifact')
    self.logs_dir = path.join(self.working_dir, 'logs')
    self.test_dir = path.join(self.working_dir, 'test')
    self.check_dir = path.join(self.working_dir, 'check')
    self.requirements_manager = package_manager(path.join(self.working_dir, 'requirements'), env.artifact_manager)
    self.stage_lib_dir = path.join(self.stage_dir, 'lib')
    self.stage_bin_dir = path.join(self.stage_dir, 'bin')
    self.stage_compile_instructions_dir = path.join(self.stage_lib_dir, 'rebuild_instructions')
    if self.recipe.format_version == 1:
      self._add_steps_v1()
    else:
      self._add_steps_v2()
    self.substitutions = {
      'REBUILD_BUILD_DIR': self.build_dir,
      'REBUILD_PACKAGE_DESELFION':  self.descriptor.name,
      'REBUILD_PACKAGE_NAME':  self.descriptor.name,
      'REBUILD_PACKAGE_VERSION':  str(self.descriptor.version),
      'REBUILD_PYTHON_PLATFORM_NAME':   self.build_target.system,
      'REBUILD_REQUIREMENTS_BIN_DIR': self.requirements_manager.bin_dir,
      'REBUILD_REQUIREMENTS_DIR': self.requirements_manager.installation_dir,
      'REBUILD_REQUIREMENTS_INCLUDE_DIR': self.requirements_manager.include_dir,
      'REBUILD_REQUIREMENTS_LIB_DIR': self.requirements_manager.lib_dir,
      'REBUILD_REQUIREMENTS_SHARE_DIR': self.requirements_manager.share_dir,
      'REBUILD_SOURCE_DIR': path.abspath(self.source_dir),
      'REBUILD_STAGE_BIN_DIR': self.stage_bin_dir,
      'REBUILD_STAGE_DIR': self.stage_dir,
      'REBUILD_STAGE_FRAMEWORKS_DIR':  path.join(self.stage_dir, 'frameworks'),
      'REBUILD_STAGE_LIB_DIR': self.stage_lib_dir,
      'REBUILD_STAGE_PREFIX_DIR':  self.stage_dir,
      'REBUILD_STAGE_PYTHON_LIB_DIR':  path.join(self.stage_dir, 'lib/python'),
      'REBUILD_TEST_DIR': self.test_dir,
    }
      
  @property
  def descriptor(self):
    return self.recipe.descriptor
    
  @property
  def filename(self):
    return self.recipe.filename
    
  @property
  def properties(self):
    return self.recipe.properties
  
  def resolve_deps_caca_tool(self, include_names):
    return self.env.resolve_deps_caca_tool(self.descriptor, include_names)
  
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
    
  def _add_steps_v1(self):
    try:
      self._step_manager.add_steps(self.steps, self, self.env)
    except Exception as ex:
      print(('Caught exception loading script: %s' % (self.filename)))
      raise

  def _add_steps_v2(self):
    try:
      self._step_manager.add_steps_v2(self.steps, self, self.env)
    except Exception as ex:
      print(('Caught exception loading script: %s' % (self.filename)))
      raise

  def step_list(self, args):
    return self._step_manager.step_list(args)

  def execute(self, args):
    result = self._step_manager.execute(self, self.env, args)
    if result.success:
      self.env.checksum_manager.save_checksums(self._current_checksums(self.env.script_manager.scripts),
                                               self.descriptor,
                                               self.build_target)
    return result

  @property
  def sources(self):
    return self._script_sources()

  file_checksums = namedtuple('file_checksums', 'sources,targets')

  def _script_sources(self):
    'Return a list of sources for this script.'
    sources = []
    for step, args in self.step_list({}):
      for sources_key in step.sources_keys():
        caca = args.get(sources_key, []) or []
        if caca:
          assert isinstance(caca, list)
          from rebuild.recipe import recipe_install_file
          if check.is_recipe_install_file_seq(caca):
            sources.extend([ x.filename for x in caca])
          else:
            sources.extend(caca)
      for k, v in args.items():
        sources.extend(dependency_provider.determine_provided(v))
    sources.append(self.filename)
    sources = [ path.relpath(f) for f in sources ]
    return sorted(algorithm.unique(sources))

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
    result = []
    for source in sources:
      s = variable.substitute(source, self.substitutions)
      if path.isfile(s):
        result.append(s)
      else:
        pass #print('you suck so bad because file not found: %s' % (s))
    return result

  def _targets(self):
    return [ self.env.artifact_manager.artifact_path(self.descriptor, self.build_target) ]

  def _current_checksums(self, all_scripts):
    return self.file_checksums(file_checksum.checksums(self._sources(all_scripts)),
                               file_checksum.checksums(self._targets()))

  def needs_rebuilding(self):
    try:
      loaded_checksums = self.env.checksum_manager.load_checksums(self.descriptor,
                                                                  self.build_target)
      
      # If the stored checksums don't match the current checksums, then we 
      if loaded_checksums:
        loaded_source_filenames = file_checksum.filenames(loaded_checksums.sources)
        loaded_target_filenames = file_checksum.filenames(loaded_checksums.targets)
        current_checksums = self._current_checksums(self.env.script_manager.scripts)
        current_source_filenames = file_checksum.filenames(current_checksums.sources)
        current_target_filenames = file_checksum.filenames(current_checksums.targets)
        if current_source_filenames != current_source_filenames:
#          self.blurb('%s needs rebuilding because loaded and current source filenames are different.')
          return True

        if loaded_target_filenames != current_target_filenames:
          return True
          
      if not loaded_checksums:
        return True
      if not file_checksum.verify(loaded_checksums.sources):
        return True
      return False
    except IOError as ex:
      return True

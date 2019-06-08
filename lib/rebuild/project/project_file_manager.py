#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple
from bes.common.algorithm import algorithm
from bes.common.check import check

from bes.system.log import log
from bes.system.env_var import os_env_var
from bes.fs.file_find import file_find
from bes.fs.file_path import file_path
from bes.fs.file_util import file_util
from bes.fs.file_checksum_getter_raw import file_checksum_getter_raw
from bes.dependency.dependency_resolver import dependency_resolver
from bes.key_value.key_value_list import key_value_list

from rebuild.base.build_blurb import build_blurb

from .project_file import project_file
from .project_file_parser import project_file_parser

#from ._rebuild_testing import artifact_manager_helper

class _project_entry(namedtuple('_project_entry', 'name, filename, checksum, project_file')):

  def __new__(clazz, name, filename, checksum, project_file):
    check.check_string(name)
    check.check_string(filename)
    check.check_project_file(project_file)
    return clazz.__bases__[0].__new__(clazz, name, filename, checksum, project_file)

class _file_entry(namedtuple('_file_entry', 'filename, checksum')):

  def __new__(clazz, filename, checksum):
    check.check_string(filename)
    check.check_string(checksum)
    return clazz.__bases__[0].__new__(clazz, filename, checksum)
  
class project_file_manager(object):

  def __init__(self, checksum_getter = None):
    log.add_logging(self, 'project_file_manager')
    check.check_file_checksum_getter(checksum_getter, allow_none = True)
    checksum_getter = checksum_getter or file_checksum_getter_raw()
    build_blurb.add_blurb(self, 'rebuild')
    self._filename_map = {}
    self._projects = {}
    self._recipe_filename_to_project = {}
    self._checksum_getter = checksum_getter

  @property
  def checksum_getter(self):
    return self._checksum_getter
    
  def load_project_file(self, filename):
    filename = path.abspath(filename)
    self.log_d('loading: %s' % (filename))
#    if filename in self._filename_map:
#      raise RuntimeError('Already loaded: %s' % (filename))
    if not project_file.is_project_file(filename):
      raise RuntimeError('Not a project file: %s' % (filename))
    text = file_util.read(filename, codec = 'utf8')
    checksum = self._checksum_getter.checksum('sha256', filename)
    parser = project_file_parser(filename, text)
    project_files = parser.parse()
    for pf in project_files:
      name = pf.name
      if name in self._projects:
        if checksum == self._projects[name].checksum:
          print('already there same checksum: %s' % (filename))
          return
        else:
          raise RuntimeError('Duplicate project \"%s\" found in: %s' % (name, filename))
      self._projects[name] = _project_entry(name, filename, checksum, pf)
      for recipe in pf.recipes:
        assert len(recipe.value.value) == 1
        recipe_filename = path.join(path.dirname(pf.filename), recipe.value.value[0])
        if recipe_filename in self._recipe_filename_to_project:
          self.log_e('Overriding recipe \"%s\": %s' % (recipe_filename, pf.name))
        self._recipe_filename_to_project[recipe_filename] = pf
    self._filename_map[filename] = project_files
    self.blurb_verbose('loaded project file %s' % (path.relpath(filename)))
    
  def load_project_files_from_env(self):
    from_env = self.find_env_project_files()
    for f in from_env:
      self.log_d('loading from env: %s' % (f))
      self.load_project_file(f)
        
  def print_projects(self):
    for name in sorted(self._projects.keys()):
      entry = self._projects[name]
      print('%s - %s\n%s\n' % (entry.name, entry.filename, str(entry.project_file)))
      
  def print_dep_map(self, build_target):
    check.check_build_target(build_target)
    dep_map = self._make_dep_map(self._projects, build_target)
    for name, imports in sorted(dep_map.items()):
      print('%s: %s' % (name, ' '.join(list(imports))))

  def resolve_project_files(self, filename, build_target):
    'Return the complete list of project_files including imports for a given project filename.'
    check.check_string(filename)
    check.check_build_target(build_target)
    filename = path.abspath(filename)
    project_files = self._filename_map.get(filename, None)
    if not project_files:
      raise RuntimeError('Filename not loaded: %s' % (filename))
    names = [ pf.name for pf in project_files ]
    dep_map = self._make_dep_map(self._projects, build_target)
    resolved_names = dependency_resolver.resolve_deps(dep_map, names)
    return [ self._projects[name].project_file for name in resolved_names ]

  def imported_projects(self, filename, build_target):
    'Return the list of recipes the given project file imports.'
    filename = path.abspath(filename)
    check.check_string(filename)
    check.check_build_target(build_target)
    pfiles = self.resolve_project_files(filename, build_target)
    imported_pfiles = [ pf for pf in pfiles if pf.filename != filename ]
    return algorithm.unique([ pf.filename for pf in imported_pfiles ])
    
  def available_recipes_dict(self, filename, build_target):
    check.check_build_target(build_target)
    filename = path.abspath(filename)
    result = {}
    project_files = self.resolve_project_files(filename, build_target)
    for pf in project_files:
      if pf.filename not in result:
        result[pf.filename] = set()
      recipes = pf.resolve_recipes(build_target.system)
      recipes = [ path.join(path.dirname(pf.filename), r) for r in recipes ]
      for r in recipes:
        result[pf.filename].add(r)
    return result

  def available_recipes(self, filename, build_target):
    check.check_build_target(build_target)
    recipes = []
    project_files = self.resolve_project_files(filename, build_target)
    for pf in project_files:
      more_recipes = pf.resolve_recipes(build_target.system)
      more_recipes = [ path.join(path.dirname(pf.filename), r) for r in more_recipes ]
      recipes.extend(more_recipes)
    return recipes
  
  def imported_recipes(self, filename, build_target):
    check.check_build_target(build_target)
    imported_projects = self.imported_projects(filename, build_target)
    available = self.available_recipes_dict(filename, build_target)
    result = []
    for p in imported_projects:
      assert p in available
      result.extend(available[p])
    return result
    
  def available_variables(self, filename, build_target):
    check.check_build_target(build_target)
    variables = key_value_list()
    project_files = self.resolve_project_files(filename, build_target)
    for pf in project_files:
      variables.extend(pf.variables)
    return variables
  
  @classmethod
  def _make_dep_map(clazz, projects, build_target):
    dep_map = {}
    for name in projects.keys():
      entry = projects[name]
      imports = entry.project_file.resolve_imports(build_target.system)
      dep_map[name] = set(imports)
    return dep_map

  @classmethod
  def find_env_project_files(clazz):
    return file_path.glob(os_env_var('REBUILD_RECIPE_PATH').path, '*.reproject')

  def override_projects(self, override_filename):
    if not override_filename:
      return
    text = file_util.read(override_filename)
    parser = project_file_parser(override_filename, text)
    override_project_files = parser.parse()
    for override_pf in override_project_files:
      if not override_pf.name in self._projects:
        self.log_e('Project for overriding not found: %s' % (override_pf.name))
        return False
      if not self._override_project(self._projects[override_pf.name].project_file, override_pf):
        return False
    return True
    
  def _override_project(self, pf, override_pf):
    assert pf.name == override_pf.name
    msg = 'overriding %s:%s with %s:%s' % (path.relpath(pf.filename), pf.name, path.relpath(override_pf.filename), override_pf.name)
    self.log_d(msg)
    self.blurb(msg)
    pf.variables.update(override_pf.variables)
    return True
    
  def print_variables(self):
    for name in sorted(self._projects.keys()):
      pf = self._projects[name].project_file
      for v in pf.variables:
        print('%s %s %s' % (path.relpath(pf.filename), pf.name, str(v)))
    
check.register_class(project_file_manager, include_seq = False)

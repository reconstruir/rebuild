#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple
from bes.common import check

from bes.system import log, os_env_var
from bes.fs import file_find, file_path, file_util
from bes.dependency import dependency_resolver
from bes.key_value import key_value_list

from rebuild.base import build_blurb

from .project_file import project_file
from .project_file_parser import project_file_parser

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

  def __init__(self):
    log.add_logging(self, 'project_file_manager')
    build_blurb.add_blurb(self, 'rebuild')
    self._filename_map = {}
    self._projects = {}

  def load_project_file(self, filename):
    filename = path.abspath(filename)
    self.log_d('loading: %s' % (filename))
#    if filename in self._filename_map:
#      raise RuntimeError('Already loaded: %s' % (filename))
    if not project_file.is_project_file(filename):
      raise RuntimeError('Not a project file: %s' % (filename))
    text = file_util.read(filename)
    checksum = file_util.checksum('sha256', filename)
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
    self._filename_map[filename] = project_files
    self.blurb('loaded project file %s' % (path.relpath(filename)))
    
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

  def available_recipes(self, filename, build_target):
    check.check_build_target(build_target)
    recipes = []
    project_files = self.resolve_project_files(filename, build_target)
    for pf in project_files:
      more_recipes = pf.resolve_recipes(build_target.system)
      more_recipes = [ path.join(path.dirname(pf.filename), r) for r in more_recipes ]
      recipes.extend(more_recipes)
    return recipes
  
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
    for name in projects.iterkeys():
      entry = projects[name]
      imports = entry.project_file.resolve_imports(build_target.system)
      dep_map[name] = set(imports)
    return dep_map

  
  @classmethod
  def find_env_project_files(clazz):
    return file_path.glob(os_env_var('REBUILD_RECIPE_PATH').path, '*.reproject')
  
check.register_class(project_file_manager, include_seq = False)

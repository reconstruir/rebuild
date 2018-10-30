#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple
from bes.common import check, node
from bes.text import white_space
from bes.fs import file_util, temp_file

from rebuild.base import build_target, package_descriptor
from rebuild.package import package
from rebuild.toolchain import compiler

class fake_package_recipe(namedtuple('fake_package_recipe', 'metadata, files, env_files, requirements, properties, objects')):
  'Class to describe a fake package.  Fake packages are use for unit testing.'
  
  def __new__(clazz, metadata, files, env_files, requirements, properties, objects):
    files = files or []
    env_files = env_files or []
    requirements = requirements or []
    properties = properties or {}
    check.check_artifact_descriptor(metadata)
    check.check_temp_item_seq(files)
    check.check_temp_item_seq(env_files)
    check.check_requirement_list(requirements)
    check.check_dict(properties)
    objects = objects or {}
    check.check_dict(objects)
    return clazz.__bases__[0].__new__(clazz, metadata, files, env_files, requirements, properties, objects)

  def __str__(self):
    return self.to_string()

  def to_string(self, depth = 0, indent = 2):
    s = self._to_node().to_string(depth = depth, indent = indent).strip()
    return white_space.shorten_multi_line_spaces(s)
  
  def _to_node(self):
    'A convenient way to make a recipe string is to build a graph first.'
    root = node('fake_package')
    metadata = root.add_child('metadata')
    for field in self.metadata._fields:
      value = getattr(self.metadata, field)
      metadata.add_child('{field} {value}'.format(field = field, value = getattr(self.metadata, field)))
    if self.files:
      self._temp_item_seq_to_node('files', self.files)
      root.add_child('')
    if self.env_files:
      self._temp_item_seq_to_node('env_files', self.env_files)
      root.add_child('')
    if self.requirements:
      root.children.append(self._requirements_to_node('requirements', self.requirements))
      root.add_child('')
    if self.properties:
      root.children.append(self._properties_to_node(self.properties))
      root.add_child('')
    return root

  @classmethod
  def _temp_item_seq_to_node(clazz, label, items):
    result = node(label)
    for item in items:
      check.check_temp_item(item)
      item_node = result.add_child(item.filename)
      for line in item.content.split('\n'):
        item_node.add_child(line)
    return result
  
  @classmethod
  def _requirements_to_node(clazz, label, requirements):
    result = node(label)
    for req in requirements:
      result.add_child(req.to_string_colon_format())
    return result
  
  @classmethod
  def _properties_to_node(clazz, properties):
    properties_node = node('properties')
    for key in sorted([ key for key in properties.keys()]):
      clazz._property_to_node(properties_node, key, properties)
    return properties_node

  @classmethod
  def _property_to_node(clazz, properties_node, key, properties):
    assert isinstance(properties_node, node)
    assert key in properties
    value = properties[key]
    properties_node.children.append(node('%s=%s' % (key, value)))

  def create_package(self, filename, debug = False):
    tmp_dir = temp_file.make_temp_dir(delete = not debug)
    if debug:
      print('tmp_dir: %s' % (tmp_dir))
    files_dir = path.join(tmp_dir, 'files')
    env_files_dir = path.join(tmp_dir, 'env')
    file_util.mkdir(files_dir)
    file_util.mkdir(env_files_dir)
    temp_file.write_temp_files(files_dir, self.files)
    temp_file.write_temp_files(env_files_dir, self.env_files)

    tmp_compiler_dir = path.join(tmp_dir, 'objects')
    
    c_programs = self.objects.get('c_programs', [])
    for c_program in c_programs:
      sources, headers = c_program.write_files(tmp_compiler_dir)
      cc = compiler(build_target.make_host_build_target())
      targets = cc.compile_c(sources)
      exe_filename = path.join(tmp_compiler_dir, c_program.filename, path.basename(c_program.filename))
      exe = cc.link_exe(exe_filename, [ target.object for target in targets ])
      file_util.copy(exe, path.join(files_dir, c_program.filename))
      
    pkg_desc = package_descriptor(self.metadata.name,
                                  self.metadata.build_version,
                                  properties = self.properties,
                                  requirements = self.requirements)
    return package.create_package(filename, pkg_desc, self.metadata.build_target, tmp_dir)

  def clone_with_mutations(self, metadata_mutations):
    metadata = self.metadata.clone_with_mutations(metadata_mutations)
    return self.__class__(metadata, self.files, self.env_files, self.requirements, self.properties, self.objects)

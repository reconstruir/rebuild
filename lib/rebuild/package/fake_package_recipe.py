#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple
from bes.common import check, node
from bes.text import white_space
from bes.fs import temp_file

from rebuild.base import package_descriptor
from .package import package

class fake_package_recipe(namedtuple('fake_package_recipe', 'metadata, files, env_files, requirements, properties')):
  'Class to describe a fake package.  Fake packages are use for unit testing.'
  
  def __new__(clazz, metadata, files, env_files, requirements, properties):
    check.check_artifact_descriptor(metadata)
    check.check_temp_item_seq(files)
    check.check_temp_item_seq(env_files)
    check.check_requirement_list(requirements)
    check.check_dict(properties)
    return clazz.__bases__[0].__new__(clazz, metadata, files, env_files, requirements, properties)

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

  @classmethod
  def _system_specific_property_to_node(clazz, key, properties):
    assert key in properties
    value = properties[key]
    assert isinstance(value, list)
    child = node(key)
    for i in value:
      child.add_child(i)
    return child

  @classmethod
  def _steps_to_node(clazz, steps):
    result = node('steps')
    for step in steps:
      step_node = result.add_child(step.name)
      for value in step.values:
        if len(value.values) == 1 and value.values[0].mask is None:
          step_node.add_child(str(value))
        else:
          value_node = step_node.add_child(value.key)
          for masked_value in value.values:
            masked_value_node = value_node.add_child(masked_value.to_string(quote = False))
      result.add_child('')
    return result

  @classmethod
  def _masked_value_list_to_node(clazz, key, mvl):
    result = node(key)
    for mv in mvl:
      result.add_child(mv.to_string())
    return result

  @classmethod
  def _load_to_node(clazz, load):
    result = node('load')
    for l in load:
      result.add_child(l)
    return result

  def create_package(self, filename):
    tmp_dir = temp_file.make_temp_dir()
    temp_file.write_temp_files(path.join(tmp_dir, 'files'), self.files)
    temp_file.write_temp_files(path.join(tmp_dir, 'env'), self.env_files)
    pkg_desc = package_descriptor(self.metadata.name,
                                  self.metadata.build_version,
                                  properties = self.properties,
                                  requirements = self.requirements)
    return package.create_package(filename, pkg_desc, self.metadata.build_target, tmp_dir)

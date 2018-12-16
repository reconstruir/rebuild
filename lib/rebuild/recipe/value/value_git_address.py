#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.compat import StringIO
from bes.git import git_address
from .value_base import value_base

class value_git_address(value_base):

  def __init__(self, origin = None, value = None, properties = None):
    super(value_git_address, self).__init__(origin, properties = properties)
    if value:
      check.check_git_address(value)
    self.value = value

  def __eq__(self, other):
    return self.value == other.value

  @property
  def address(self):
    return self.substitute(self.value.address)
  
  @property
  def revision(self):
    return self.substitute(self.value.revision)
  
  #@abstractmethod
  def value_to_string(self, quote, include_properties = True):
    buf = StringIO()
    buf.write(self.address)
    buf.write(' ')
    buf.write(self.revision)
    self._append_properties_string(buf, include_properties)
    return buf.getvalue()

  #@abstractmethod
  def sources(self, recipe_env):
    'Return a list of sources this caca provides or None if no sources.'
    return [ self.downloaded_tarball_path(recipe_env) ]

  #@abstractmethod
  def substitutions_changed(self):
    pass
  
  @classmethod
  #@abstractmethod
  def parse(clazz, origin, text, node):
    if origin:
      check.check_value_origin(origin)
    check.check_node(node)
    parts = string_util.split_by_white_space(text)
    if len(parts) < 2:
      raise ValueError('%s: expected address and revision instead of: %s' % (origin, text))
    address = parts[0]
    revision = parts[1]
    rest = string_util.replace(text, { address: '', revision: '' })
    properties = clazz.parse_properties(rest)
    return clazz(origin = origin, value = git_address(address, revision), properties = properties)
  
  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    return None

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    # FIXME
    return values[-1]
  
  def downloaded_tarball_path(self, recipe_env):
    return recipe_env.git_downloads_manager.tarball_path(self.address, self.revision)
  
  def download(self, recipe_env):
    if not recipe_env.git_downloads_manager.has_tarball(self.address, self.revision):
      assert self.needs_download(recipe_env)
      recipe_env.git_downloads_manager.get_tarball(self.address, self.revision)
    assert not self.needs_download(recipe_env)

  def needs_download(self, recipe_env):
    return not path.isfile(self.downloaded_tarball_path(recipe_env))
    
check.register_class(value_git_address, include_seq = False)

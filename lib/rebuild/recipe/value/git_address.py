#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.compat import StringIO
from bes.dependency import dependency_provider
from .value_base import value_base

class git_address(value_base):

  def __init__(self, env = None, address = '', revision = ''):
    super(git_address, self).__init__(env)
    check.check_string(address)
    check.check_string(revision)
    self.address = address
    self.revision = revision

  def __str__(self):
    return self.value_to_string()
    
  def __eq__(self, other):
    return self.address == other.address and self.revision == other.revision
    
  def value_to_string(self):
    buf = StringIO()
    buf.write(self.address)
    buf.write(' ')
    buf.write(self.revision)
    return buf.getvalue()

  #@abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    return [ self.downloaded_tarball_path() ]

  @classmethod
  #@abstractmethod
  def parse(clazz, env, recipe_filename, value):
    parts = string_util.split_by_white_space(value)
    if len(parts) != 2:
      raise ValueError('expected address and tag instead of: %s' % (value))
    return clazz(env, parts[0], parts[1])
  
  @classmethod
  #@abstractmethod
  def default_value(clazz):
    return None

  def downloaded_tarball_path(self):
    return self.env.downloads_manager.tarball_path(self.address, self.revision)
  
  def download(self):
    if not self.env.downloads_manager.has_tarball(self.address, self.revision):
      assert self.needs_download()
      self.env.downloads_manager.get_tarball(self.address, self.revision)
    assert not self.needs_download()

  def needs_download(self):
    return not path.isfile(self.downloaded_tarball_path())
    
check.register_class(git_address, include_seq = False)

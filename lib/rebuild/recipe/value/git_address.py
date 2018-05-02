#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, string_util
from bes.compat import StringIO
from bes.dependency import dependency_provider
from .value_base import value_base

class git_address(value_base):

  def __init__(self, env, address, revision):
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
    return [ self.env.downloads_manager.tarball_path(self.address, self.revision) ]

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
  
check.register_class(git_address, include_seq = False)

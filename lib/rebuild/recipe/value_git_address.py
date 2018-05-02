#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, string_util
from bes.compat import StringIO
from bes.dependency import dependency_provider
from .recipe_caca import recipe_caca

class value_git_address(recipe_caca):

  def __init__(self, env, address, revision):
    super(value_git_address, self).__init__(env)
    check.check_string(address)
    check.check_string(revision)
    self.address = address
    self.revision = revision

  def __str__(self):
    return self.value_to_string()
    
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
  
check.register_class(value_git_address, include_seq = False)

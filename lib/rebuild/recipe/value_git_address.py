#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, string_util
from bes.compat import StringIO
from bes.dependency import dependency_provider

class value_git_address(dependency_provider):

  # Needs to be set for parse to work
  download_manager = None
  
  def __init__(self, download_manager, address, revision):
    assert download_manager
    check.check_string(address)
    check.check_string(revision)
    self._download_manager = download_manager
    self.address = address
    self.revision = revision

  def __str__(self):
    return self.value_to_string()
    
  def value_to_string(self):
    buf = StringIO()
    buf.write(self.address)
    buf.write(',')
    buf.write(self.revision)
    return buf.getvalue()
    
  def provided(self):
    'Return a list of dependencies provided by this provider.'
    return [ self._download_manager.tarball_path(self.address, self.revision) ]

  @classmethod
  def parse(clazz, value):
    parts = string_util.split_by_white_space(value)
    if len(parts) != 2:
      raise ValueError('expected address and tag instead of: %s' % (value))
    return clazz(self.download_manager, parts[0], parts[1])
  
check.register_class(value_git_address, include_seq = False)

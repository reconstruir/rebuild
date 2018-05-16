#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.compat import StringIO
from bes.key_value import key_value_list
from .value_base import value_base

class value_git_address(value_base):

  def __init__(self, env = None, origin = None, address = '', revision = '', properties = None):
    super(value_git_address, self).__init__(env , origin, properties = properties)
    check.check_string(address)
    check.check_string(revision)
    self._address = address
    self._revision = revision

  def __eq__(self, other):
    return self._address == other._address and self._revision == other._revision

  @property
  def address(self):
    return self.substitute(self._address)
  
  @property
  def revision(self):
    return self.substitute(self._revision)
  
  #@abstractmethod
  def value_to_string(self, quote):
    buf = StringIO()
    buf.write(self.address)
    buf.write(' ')
    buf.write(self.revision)
    ps = self.properties_to_string()
    if ps:
      buf.write(' ')
      buf.write(ps)
    return buf.getvalue()

  #@abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    return [ self.downloaded_tarball_path() ]

  #@abstractmethod
  def substitutions_changed(self):
    pass
  
  @classmethod
  #@abstractmethod
  def parse(clazz, env, origin, text):
    parts = string_util.split_by_white_space(text)
    if len(parts) < 2:
      raise ValueError('%s: expected address and revision instead of: %s' % (origin, text))
    address = parts[0]
    revision = parts[1]
    rest = string_util.replace(text, { address: '', revision: '' })
    properties = clazz.parse_properties(rest)
    return clazz(env, origin = origin, address = address, revision = revision, properties = properties)
  
  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    return None

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    # FIXME
    return values[-1]
  
  def downloaded_tarball_path(self):
    return self.env.downloads_manager.tarball_path(self.address, self.revision)
  
  def download(self):
    if not self.env.downloads_manager.has_tarball(self.address, self.revision):
      assert self.needs_download()
      self.env.downloads_manager.get_tarball(self.address, self.revision)
    assert not self.needs_download()

  def needs_download(self):
    return not path.isfile(self.downloaded_tarball_path())
    
check.register_class(value_git_address, include_seq = False)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system import logger
from bes.common.check import check
from bes.common.string_util import string_util
from bes.common.time_util import time_util
from bes.compat import StringIO
from bes.git import git_address
from bes.git import git
from bes.key_value import key_value

from .value_base import value_base

_LOG = logger('value_git_address')

class value_git_address(value_base):

  def __init__(self, origin = None, value = None, properties = None):
    super(value_git_address, self).__init__(origin, properties = properties)
    self.value = check.check_git_address(value, allow_none = True)
    
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
  def sources(self, recipe_env, variables):
    'Return a list of sources this value provides or None if no sources.'
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
    address = path.expanduser(address)
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
    if self.revision == '[DIR]':
      result = recipe_env.source_dir_zipballs.get_tarball(self.address)
    else:
      result = recipe_env.git_downloads_manager.tarball_path(self.address, self.revision)
    _LOG.log_d('downloaded_tarball_path: address=%s; revision=%s => %s' % (self.address, self.revision, path.relpath(result)))
    return result
  
  def download(self, recipe_env):
    _LOG.log_d('download: address=%s; revision=%s' % (self.address, self.revision))
    if self.revision == '[DIR]':
      return True
    if not recipe_env.git_downloads_manager.has_tarball(self.address, self.revision):
      assert self.needs_download(recipe_env)
      recipe_env.git_downloads_manager.get_tarball(self.address, self.revision)
    assert not self.needs_download(recipe_env)

  def needs_download(self, recipe_env):
    _LOG.log_d('needs_download: address=%s; revision=%s' % (self.address, self.revision))
    if self.revision == '[DIR]':
      return False
    return not path.isfile(self.downloaded_tarball_path(recipe_env))

  @classmethod
  #@abstractmethod
  def _parse_plain_string(clazz, origin, s):
    'Parse just a string.'
    try:
      return int(s)
    except Exception as ex:
      value_parsing.raise_error(origin, 'Not a valid int: \"%s\"' % (s))
  
check.register_class(value_git_address, include_seq = False)

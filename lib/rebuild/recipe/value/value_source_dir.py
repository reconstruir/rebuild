#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.compat import StringIO
from bes.archive import archiver
from .value_base import value_base

class value_source_dir(value_base):

  def __init__(self, origin = None, where = '', properties = None):
    super(value_source_dir, self).__init__(origin, properties = properties)
    check.check_string(where)
    self.where = where
    self._tarball = None
    
  def __eq__(self, other):
    return self.where == other.where
    
  #@abstractmethod
  def value_to_string(self, quote, include_properties = True):
    buf = StringIO()
    buf.write(self.where)
    self._append_properties_string(buf, include_properties)
    return buf.getvalue()

  #@abstractmethod
  def sources(self, recipe_env):
    'Return a list of sources this caca provides or None if no sources.'
    return [ self._tarball ]

  #@abstractmethod
  def substitutions_changed(self):
    self._update_tarball_path()
  
  @classmethod
  #@abstractmethod
  def parse(clazz, origin, text, node):
    if origin:
      check.check_value_origin(origin)
    check.check_node(node)
    parts = string_util.split_by_white_space(text)
    if len(parts) < 1:
      raise ValueError('%s: expected filename instead of: %s' % (origin, text))
    where = parts[0]
    rest = string_util.replace(text, { where: '' })
    properties = clazz.parse_properties(rest)
    return clazz(origin = origin, where = where, properties = properties)
  
  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    return None

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    # FIXME
    return values[-1]
  
  def _update_tarball_path(self):
    assert self.substitutions
    temp_dir = self.substitute('${REBUILD_TEMP_DIR}')
    self._full_name = self.substitute('${REBUILD_PACKAGE_FULL_NAME}')
    self._resolved_where = self.substitute(self.where)
    tarball_filename = '%s.tar.gz' % (self._full_name)
    self._tarball = path.join(temp_dir, tarball_filename)
    
  def tarball(self):
    if not path.isfile(self._tarball):
      archiver.create(self._tarball, self._resolved_where, base_dir = self._full_name)
      assert path.isfile(self._tarball)
    return self._tarball
  
check.register_class(value_source_dir, include_seq = False)

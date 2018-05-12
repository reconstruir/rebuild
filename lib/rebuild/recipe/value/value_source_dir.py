#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.compat import StringIO
from bes.key_value import key_value_list
from bes.archive import archiver
from .value_base import value_base

class value_source_dir(value_base):

  def __init__(self, env = None, origin = None, where = '', properties = None):
    super(value_source_dir, self).__init__(env, origin, properties = properties)
    check.check_string(where)
    self.where = where
    self._tarball = None
    
  def __eq__(self, other):
    return self.where == other.where
    
  #@abstractmethod
  def value_to_string(self, quote):
    buf = StringIO()
    buf.write(self.where)
    ps = self.properties_to_string()
    if ps:
      buf.write(' ')
      buf.write(ps)
    return buf.getvalue()

  #@abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    return [ self._tarball ]

  #@abstractmethod
  def substitutions_changed(self):
    self._update()
  
  @classmethod
  #@abstractmethod
  def parse(clazz, env, origin, text):
    parts = string_util.split_by_white_space(text)
    if len(parts) < 1:
      raise ValueError('%s: expected filename instead of: %s' % (origin, text))
    where = parts[0]
    rest = string_util.replace(text, { where: '' })
    properties = clazz.parse_properties(rest)
    return clazz(env = env, origin = origin, where = where, properties = properties)
  
  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    return None

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    # FIXME
    return values[-1]
  
  def _update(self):
    assert self.substitutions
    temp_dir = self.substitute('${REBUILD_TEMP_DIR}')
    full_name = self.substitute('${REBUILD_PACKAGE_FULL_NAME}')
    where = self.substitute(self.where)
    tarball_filename = '%s.tar.gz' % (full_name)
    tarball_path = path.join(temp_dir, tarball_filename)
    archiver.create(tarball_path, where, base_dir = full_name)
    assert path.isfile(tarball_path)
    self._tarball = tarball_path
  
check.register_class(value_source_dir, include_seq = False)

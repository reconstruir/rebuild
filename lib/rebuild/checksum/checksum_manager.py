#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check_type, object_util
from bes.fs import file_checksum, file_util
from rebuild.package_manager import package_descriptor
from rebuild.base import build_blurb, build_target
from collections import namedtuple

class checksum_manager(object):
  'Manage checksums.'

  file_checksums = namedtuple('file_checksums', 'sources,targets')

  CHECKSUMS_SOURCES_FILENAME = 'sources.checksums'
  CHECKSUMS_TARGETS_FILENAME = 'targets.checksums'
  
  def __init__(self, root_dir):
    check_type.check_string(root_dir, 'root_dir')
    build_blurb.add_blurb(self, label = 'build')
    self._root_dir = root_dir
    self._build_target = build_target
    self._ignored = set()
    self._ignore_all = False
    self._sources = {}

  @property
  def root_dir(self):
    return self._root_dir
    
  @property
  def ignore_all(self):
    return self._ignore_all
    
  @ignore_all.setter
  def ignore_all(self, ignore_all):
    self._ignore_all = ignore_all

  def ignore(self, name):
    self._ignored.add(name)

  def is_ignored(self, name):
    return self._ignore_all or name in self._ignored

  def set_sources(self, name, sources):
    assert False
    self._sources[name] = sources

  def print_sources(self):
    for name, sources in sorted(self._sources.items()):
      print('%s:' % (name))
      for source in sources:
        print('  %s' % (source))

  def remove_checksums(self, packages, bt):
    packages = object_util.listify(packages)
    assert package_descriptor.is_package_info_list(packages)
    checksum_dirs = [ self._checksum_dir(pd, bt) for pd in packages ]
    for d in checksum_dirs:
      self.blurb('removing checksums: %s' % (path.relpath(d)))
    file_util.remove(checksum_dirs)

  def _checksum_dir(self, pd, bt):
    check_type.check(pd, package_descriptor, 'package_descriptor')
    check_type.check(bt, build_target, 'build_target')
    return path.join(self._root_dir, bt.build_path, pd.full_name)

  def load_checksums(self, pd, bt):
    d = self._checksum_dir(pd, bt)
    sources = file_checksum.load_checksums(path.join(d, self.CHECKSUMS_SOURCES_FILENAME))
    targets = file_checksum.load_checksums(path.join(d, self.CHECKSUMS_TARGETS_FILENAME))
    if not sources and not targets:
      return None
    return self.file_checksums(sources, targets)

  def save_checksums(self, checksums, pd, bt):
    d = self._checksum_dir(pd, bt)
    file_checksum.save_checksums(path.join(d, self.CHECKSUMS_SOURCES_FILENAME), checksums.sources)
    file_checksum.save_checksums(path.join(d, self.CHECKSUMS_TARGETS_FILENAME), checksums.targets)

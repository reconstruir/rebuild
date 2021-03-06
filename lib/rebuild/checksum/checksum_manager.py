#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, object_util
from bes.fs import file_checksum_list, file_util
from rebuild.base import build_blurb, build_target, package_descriptor
from collections import namedtuple

class checksum_manager(object):
  'Manage checksums.'

  file_checksums = namedtuple('file_checksums', 'sources,targets')

  CHECKSUMS_SOURCES_FILENAME = 'sources.checksums'
  CHECKSUMS_TARGETS_FILENAME = 'targets.checksums'
  
  def __init__(self, root_dir):
    check.check_string(root_dir)
    build_blurb.add_blurb(self, label = 'rebuild')
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

  def remove_checksums(self, packages, level):
    packages = object_util.listify(packages)
    check.check_package_descriptor_seq(packages)
    checksum_dirs = [ self._checksum_dir(pd, level) for pd in packages ]
    for d in checksum_dirs:
      self.blurb('removing checksums: %s' % (path.relpath(d)))
    file_util.remove(checksum_dirs)

  def _checksum_dir(self, pd, level):
    check.check_package_descriptor(pd)
    check.check(level, build_target)
    return path.join(self._root_dir, level.build_path, pd.full_name)

  def load_checksums(self, pd, level):
    d = self._checksum_dir(pd, level)
    sources = file_checksum_list.load_checksums_file(path.join(d, self.CHECKSUMS_SOURCES_FILENAME))
    targets = file_checksum_list.load_checksums_file(path.join(d, self.CHECKSUMS_TARGETS_FILENAME))
    if not sources and not targets:
      return None
    return self.file_checksums(sources, targets)

  def save_checksums(self, checksums, pd, level):
    d = self._checksum_dir(pd, level)
    checksums.sources.save_checksums_file(path.join(d, self.CHECKSUMS_SOURCES_FILENAME))
    checksums.targets.save_checksums_file(path.join(d, self.CHECKSUMS_TARGETS_FILENAME))

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.archive import archiver
from bes.common import check_type
from .tarball_finder import tarball_finder

class source_finder(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def find_source(self, name, version, build_target):
    pass

  @classmethod
  def _find_tarball(clazz, where, name, version, system):
    check_type.check_string(name, 'name')
    check_type.check_string(version, 'version')
    check_type.check_string(system, 'system')

    tarball = tarball_finder.find(where, name, version)

    # If we find more than one tarball it could be because there are 1 for each platform so
    # filter out only the ones that match the current build system target
    if len(tarball) > 1:
      pattern = '/%s/' % (system)
      system_specific_tarball = [ t for t in tarball if pattern in t ]
      if system_specific_tarball:
        tarball = system_specific_tarball
      
    if len(tarball) > 1:
      raise RuntimeError('Too many tarballs found for %s-%s: %s' % (name, version, ' '.join(tarball)))
    if len(tarball) == 0:
      return None

    tarball = tarball[0]

    clazz._check_archive_valid(tarball)

    return tarball

  @classmethod
  def _check_archive_valid(clazz, filename):
    if not archiver.is_valid(filename):
      raise RuntimeError('Invalid archive type: %s' % (filename))

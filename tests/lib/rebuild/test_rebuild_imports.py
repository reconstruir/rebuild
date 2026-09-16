#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.testing.unit_test import unit_test
from bes.testing.package_imports import package_imports

class test_rebuild_imports(unit_test):
  '''Every module under lib/rebuild imports, except the ones listed here.

  The list is a ratchet: a module that newly fails to import fails this
  test, and so does a listed one that starts importing, so the list
  only shrinks. Each entry says why it is broken.
  '''

  _LIB = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'lib')

  _KNOWN_BROKEN = {
    'rebuild.artifactory.mock_artifactory': 'imports mock_artifactory_server, which does not exist',
    'rebuild.artifactory.vfs_artifactory': 'imports bes.files.bf_checksum_db, which does not exist',
    'rebuild.toolchain._toolchain_android': 'an assertion at import time fails',
  }

  def test_every_module_imports(self):
    count = package_imports.check(self._LIB, 'rebuild', known_broken = self._KNOWN_BROKEN)
    self.assertGreater(count, 200)

if __name__ == '__main__':
  unit_test.main()

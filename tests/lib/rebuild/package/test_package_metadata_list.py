#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
import os.path as path
from bes.sqlite import sqlite
from bes.testing.unit_test import unit_test
from bes.fs import file_checksum_list as FCL
from rebuild.base import build_system, build_target, package_descriptor, requirement_list as RL
from rebuild.package import package_metadata as PM,  package_metadata_list as PML, package_files as PF
from rebuild.package import package_files

class test_package_metadata_list(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/rebuild/package'

  TEST_REQUIREMENTS = RL.parse('foo >= 1.2.3-1 bar >= 6.6.6-1')
  TEST_FILES = PF(FCL(
    [
      ( 'f1', 'fchk1' ),
      ( 'f2', 'fchk2' ),
    ]),
    FCL([
      ( 'e1', 'echk1' ),
      ( 'e2', 'echk2' ),
    ]),
    'files_chk',
    'env_files_chk')
    
  TEST_PROPERTIES = { 'p1': 'v1', 'p2': 6 }

  def test_sort(self):
    l = PML()
    l.append(self._make_md('foo', '1.0.0', 'macos', 'release'))
    l.append(self._make_md('foo', '1.0.1', 'macos', 'release'))
    l.sort()
    for x in l:
      print('X: %s' % (str(x.artifact_descriptor)))
      
  def _make_md(self, name, version, system, level):
    if system == 'macos':
      archs = [ 'x86_64' ]
    else:
      archs = [ 'x86_64' ]
    artifact = '%s-%s.tar.gz' % (name, version)
    return PM(artifact, name, version, 0, 0, system, level, archs, '', self.TEST_REQUIREMENTS, self.TEST_PROPERTIES, self.TEST_FILES)
    
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
import os.path as path
from bes.sqlite import sqlite
from bes.testing.unit_test import unit_test
from rebuild.base import requirement_list as RL
from rebuild.package import package_metadata as PM,  package_metadata_list as PML, package_files as PF
from rebuild.package import package_files
from rebuild.package.package_file_list import package_file_list as FCL

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
    l.append(self._make_md('foo', '1.0.1', 'macos', 'release'))
    l.append(self._make_md('foo', '1.0.0', 'macos', 'release'))
    l.append(self._make_md('bar', '2.0.0', 'macos', 'release'))
    l.append(self._make_md('bar', '2.0.1', 'macos', 'release'))
    l.sort()
    self.assertEqual( 'bar-2.0.0', l[0].full_name )
    self.assertEqual( 'bar-2.0.1', l[1].full_name )
    self.assertEqual( 'foo-1.0.0', l[2].full_name )
    self.assertEqual( 'foo-1.0.1', l[3].full_name )

  def test_latest_versions(self):
    l = PML()
    l.append(self._make_md('foo', '1.0.0', 'macos', 'release'))
    l.append(self._make_md('foo', '1.0.1', 'macos', 'release'))
    l.append(self._make_md('bar', '2.0.0', 'macos', 'release'))
    l.append(self._make_md('bar', '2.0.1', 'macos', 'release'))
    latest = l.latest_versions()
    self.assertEqual( 2, len(latest) )
    self.assertEqual( 'bar-2.0.1', latest[0].full_name )
    self.assertEqual( 'foo-1.0.1', latest[1].full_name )
      
  def _make_md(self, name, version, system, level):
    artifact = '%s-%s.tar.gz' % (name, version)
    return PM(artifact, name, version, 0, 0, system, level, 'x86_64', '', '', self.TEST_REQUIREMENTS, self.TEST_PROPERTIES, self.TEST_FILES)
    
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from rebuild.base.build_version import build_version

class test_version(unit_test):

  def test_upstream_version_is_valid(self):
    self.assertTrue( build_version.upstream_version_is_valid('1.2.3') )
    self.assertTrue( build_version.upstream_version_is_valid('1.2.3') )
    self.assertTrue( build_version.upstream_version_is_valid('1.2.3alpha') )
    self.assertTrue( build_version.upstream_version_is_valid('1.2.3alpha+') )
    self.assertTrue( build_version.upstream_version_is_valid('1.2.3alpha~') )
    self.assertTrue( build_version.upstream_version_is_valid('0') )
    self.assertTrue( build_version.upstream_version_is_valid('1') )
    self.assertTrue( build_version.upstream_version_is_valid('1a') )
    self.assertTrue( build_version.upstream_version_is_valid('alpha1') )
    self.assertTrue( build_version.upstream_version_is_valid('a123') )
    self.assertTrue( build_version.upstream_version_is_valid('a') )

    self.assertFalse( build_version.upstream_version_is_valid(0) )
    self.assertFalse( build_version.upstream_version_is_valid(1) )
    self.assertFalse( build_version.upstream_version_is_valid(666) )
    self.assertFalse( build_version.upstream_version_is_valid(1.2) )
    self.assertFalse( build_version.upstream_version_is_valid([]) )
    self.assertFalse( build_version.upstream_version_is_valid('') )
    self.assertFalse( build_version.upstream_version_is_valid('-1') )
    
  def test_validate_upstream_version(self):
    self.assertEqual( '1.2.3', build_version.validate_upstream_version('1.2.3') )
    self.assertEqual( '1.2.3', build_version.validate_upstream_version('1.2.3') )
    self.assertEqual( '1.2.3alpha', build_version.validate_upstream_version('1.2.3alpha') )
    self.assertEqual( '1.2.3alpha+', build_version.validate_upstream_version('1.2.3alpha+') )
    self.assertEqual( '1.2.3alpha~', build_version.validate_upstream_version('1.2.3alpha~') )
    self.assertEqual( '0', build_version.validate_upstream_version('0') )
    self.assertEqual( '1', build_version.validate_upstream_version('1') )
    self.assertEqual( '1a', build_version.validate_upstream_version('1a') )

  def test_validate_upstream_version_invalid(self):
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_upstream_version(0)
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_upstream_version(1)
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_upstream_version(666)
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_upstream_version(1.2)
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_upstream_version([])
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_upstream_version('')
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_upstream_version('-1')

  def test_epoch_is_valid(self):
    self.assertTrue( build_version.epoch_is_valid(0) )
    self.assertTrue( build_version.epoch_is_valid(1) )
    self.assertTrue( build_version.epoch_is_valid('1') )
    self.assertFalse( build_version.epoch_is_valid(1.1) )
    self.assertFalse( build_version.epoch_is_valid([]) )
    self.assertFalse( build_version.epoch_is_valid('foo') )
    self.assertFalse( build_version.epoch_is_valid('a') )
    self.assertFalse( build_version.epoch_is_valid('1.1') )
    self.assertFalse( build_version.epoch_is_valid('1a') )

  def test_validate_epoch(self):
    self.assertEqual( 0, build_version.validate_epoch(0) )
    self.assertEqual( 1, build_version.validate_epoch(1) )
    self.assertEqual( 0, build_version.validate_epoch('0') )
    self.assertEqual( 1, build_version.validate_epoch('1') )

  def test_validate_epoch_invalid(self):
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_epoch(1.1)
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_epoch([])
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_epoch('foo')
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_epoch('1.1')
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_epoch('1a')

  def test_revision_is_valid(self):
    self.assertTrue( build_version.revision_is_valid(0) )
    self.assertTrue( build_version.revision_is_valid(1) )
    self.assertTrue( build_version.revision_is_valid('1') )
    self.assertFalse( build_version.revision_is_valid(1.1) )
    self.assertFalse( build_version.revision_is_valid([]) )
    self.assertFalse( build_version.revision_is_valid('foo') )
    self.assertFalse( build_version.revision_is_valid('a') )
    self.assertFalse( build_version.revision_is_valid('1.1') )
    self.assertFalse( build_version.revision_is_valid('1a') )

  def test_validate_revision(self):
    self.assertEqual( 0, build_version.validate_revision(0) )
    self.assertEqual( 1, build_version.validate_revision(1) )
    self.assertEqual( 0, build_version.validate_revision('0') )
    self.assertEqual( 1, build_version.validate_revision('1') )

  def test_validate_revision_invalid(self):
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_revision(1.1)
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_revision([])
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_revision('foo')
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_revision('1.1')
    with self.assertRaises(RuntimeError) as context:
      build_version.validate_revision('1a')

  def test___str__(self):
    self.assertEqual( '1.2.3', str(build_version('1.2.3', 0, 0)) )
    self.assertEqual( '1.2.3-1', str(build_version('1.2.3', 1, 0)) )
    self.assertEqual( '1:1.2.3-1', str(build_version('1.2.3', 1, 1)) )

  def test_parse(self):
    self.assertEqual( build_version('1.2.3', 0, 0), build_version.parse('1.2.3') )
    self.assertEqual( build_version('1.2.3', 1, 0), build_version.parse('1.2.3-1') )
    self.assertEqual( build_version('1.2.3', 0, 1), build_version.parse('1:1.2.3') )
    self.assertEqual( build_version('1.2.3', 1, 2), build_version.parse('2:1.2.3-1') )

  def test_parse_invalid(self):
    with self.assertRaises(RuntimeError) as context:
      build_version.parse(':1.2.3')
    with self.assertRaises(RuntimeError) as context:
      build_version.parse('a:1.2.3')
    with self.assertRaises(RuntimeError) as context:
      build_version.parse('1.2.3-')
    with self.assertRaises(RuntimeError) as context:
      build_version.parse('1.2.3-a')
    with self.assertRaises(RuntimeError) as context:
      build_version.parse('1:2:3')

  def test_cmp(self):
    self.assertEqual( -1, self._call_cmp('1.2.3', '1.2.4') )
    self.assertEqual( 0, self._call_cmp('1.2.3', '1.2.3') )
    self.assertEqual( 1, self._call_cmp('1.2.4', '1.2.3') )
    self.assertEqual( -1, self._call_cmp('1.2.8', '1.2.9') )
    self.assertEqual( -1, self._call_cmp('1.2.10', '1.2.11') )
    self.assertEqual( -1, self._call_cmp('1.2.9', '1.2.10') )
    
    self.assertEqual( 1, self._call_cmp('1:1.2.3', '1.2.4') )
    self.assertEqual( -1, self._call_cmp('0:1.2.3', '1.2.4') )
    self.assertEqual( -1, self._call_cmp('0:1.2.3', '0:1.2.3-1') )
    self.assertEqual( 1, self._call_cmp('0:1.2.3-3', '0:1.2.3-2') )
    self.assertEqual( 1, self._call_cmp('1.2.3.alpha1', '1.2.3') )

  def _call_cmp(self, v1, v2):
    return build_version.compare(build_version.parse(v1), build_version.parse(v2))

if __name__ == "__main__":
  unit_test.main()

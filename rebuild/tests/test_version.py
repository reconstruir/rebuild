#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.unit_test import unit_test
from rebuild import version

class test_version(unit_test):

  def test_upstream_version_is_valid(self):
    self.assertTrue( version.upstream_version_is_valid('1.2.3') )
    self.assertTrue( version.upstream_version_is_valid('1.2.3') )
    self.assertTrue( version.upstream_version_is_valid('1.2.3alpha') )
    self.assertTrue( version.upstream_version_is_valid('1.2.3alpha+') )
    self.assertTrue( version.upstream_version_is_valid('1.2.3alpha~') )
    self.assertTrue( version.upstream_version_is_valid('0') )
    self.assertTrue( version.upstream_version_is_valid('1') )
    self.assertTrue( version.upstream_version_is_valid('1a') )

    self.assertFalse( version.upstream_version_is_valid(0) )
    self.assertFalse( version.upstream_version_is_valid(1) )
    self.assertFalse( version.upstream_version_is_valid(666) )
    self.assertFalse( version.upstream_version_is_valid(1.2) )
    self.assertFalse( version.upstream_version_is_valid([]) )
    self.assertFalse( version.upstream_version_is_valid('') )
    self.assertFalse( version.upstream_version_is_valid('-1') )
    self.assertFalse( version.upstream_version_is_valid('alpha1') )
    self.assertFalse( version.upstream_version_is_valid('a123') )
    self.assertFalse( version.upstream_version_is_valid('a') )
    
  def test_validate_upstream_version(self):
    self.assertEqual( '1.2.3', version.validate_upstream_version('1.2.3') )
    self.assertEqual( '1.2.3', version.validate_upstream_version('1.2.3') )
    self.assertEqual( '1.2.3alpha', version.validate_upstream_version('1.2.3alpha') )
    self.assertEqual( '1.2.3alpha+', version.validate_upstream_version('1.2.3alpha+') )
    self.assertEqual( '1.2.3alpha~', version.validate_upstream_version('1.2.3alpha~') )
    self.assertEqual( '0', version.validate_upstream_version('0') )
    self.assertEqual( '1', version.validate_upstream_version('1') )
    self.assertEqual( '1a', version.validate_upstream_version('1a') )

  def test_validate_upstream_version_invalid(self):
    with self.assertRaises(RuntimeError) as context:
      version.validate_upstream_version(0)
    with self.assertRaises(RuntimeError) as context:
      version.validate_upstream_version(1)
    with self.assertRaises(RuntimeError) as context:
      version.validate_upstream_version(666)
    with self.assertRaises(RuntimeError) as context:
      version.validate_upstream_version(1.2)
    with self.assertRaises(RuntimeError) as context:
      version.validate_upstream_version([])
    with self.assertRaises(RuntimeError) as context:
      version.validate_upstream_version('')
    with self.assertRaises(RuntimeError) as context:
      version.validate_upstream_version('-1')
    with self.assertRaises(RuntimeError) as context:
      version.validate_upstream_version('alpha1')
    with self.assertRaises(RuntimeError) as context:
      version.validate_upstream_version('a123')
    with self.assertRaises(RuntimeError) as context:
      version.validate_upstream_version('a')

  def test_epoch_is_valid(self):
    self.assertTrue( version.epoch_is_valid(0) )
    self.assertTrue( version.epoch_is_valid(1) )
    self.assertTrue( version.epoch_is_valid('1') )
    self.assertFalse( version.epoch_is_valid(1.1) )
    self.assertFalse( version.epoch_is_valid([]) )
    self.assertFalse( version.epoch_is_valid('foo') )
    self.assertFalse( version.epoch_is_valid('a') )
    self.assertFalse( version.epoch_is_valid('1.1') )
    self.assertFalse( version.epoch_is_valid('1a') )

  def test_validate_epoch(self):
    self.assertEqual( 0, version.validate_epoch(0) )
    self.assertEqual( 1, version.validate_epoch(1) )
    self.assertEqual( 0, version.validate_epoch('0') )
    self.assertEqual( 1, version.validate_epoch('1') )

  def test_validate_epoch_invalid(self):
    with self.assertRaises(RuntimeError) as context:
      version.validate_epoch(1.1)
    with self.assertRaises(RuntimeError) as context:
      version.validate_epoch([])
    with self.assertRaises(RuntimeError) as context:
      version.validate_epoch('foo')
    with self.assertRaises(RuntimeError) as context:
      version.validate_epoch('1.1')
    with self.assertRaises(RuntimeError) as context:
      version.validate_epoch('1a')

  def test_revision_is_valid(self):
    self.assertTrue( version.revision_is_valid(0) )
    self.assertTrue( version.revision_is_valid(1) )
    self.assertTrue( version.revision_is_valid('1') )
    self.assertFalse( version.revision_is_valid(1.1) )
    self.assertFalse( version.revision_is_valid([]) )
    self.assertFalse( version.revision_is_valid('foo') )
    self.assertFalse( version.revision_is_valid('a') )
    self.assertFalse( version.revision_is_valid('1.1') )
    self.assertFalse( version.revision_is_valid('1a') )

  def test_validate_revision(self):
    self.assertEqual( 0, version.validate_revision(0) )
    self.assertEqual( 1, version.validate_revision(1) )
    self.assertEqual( 0, version.validate_revision('0') )
    self.assertEqual( 1, version.validate_revision('1') )

  def test_validate_revision_invalid(self):
    with self.assertRaises(RuntimeError) as context:
      version.validate_revision(1.1)
    with self.assertRaises(RuntimeError) as context:
      version.validate_revision([])
    with self.assertRaises(RuntimeError) as context:
      version.validate_revision('foo')
    with self.assertRaises(RuntimeError) as context:
      version.validate_revision('1.1')
    with self.assertRaises(RuntimeError) as context:
      version.validate_revision('1a')

  def test___str__(self):
    self.assertEqual( '1.2.3', str(version('1.2.3', 0, 0)) )
    self.assertEqual( '1.2.3-1', str(version('1.2.3', 1, 0)) )
    self.assertEqual( '1:1.2.3-1', str(version('1.2.3', 1, 1)) )

  def test_parse(self):
    self.assertEqual( version('1.2.3', 0, 0), version.parse('1.2.3') )
    self.assertEqual( version('1.2.3', 1, 0), version.parse('1.2.3-1') )
    self.assertEqual( version('1.2.3', 0, 1), version.parse('1:1.2.3') )
    self.assertEqual( version('1.2.3', 1, 1), version.parse('1:1.2.3-1') )

  def test_parse_invalid(self):
    with self.assertRaises(RuntimeError) as context:
      version.parse(':1.2.3')
    with self.assertRaises(RuntimeError) as context:
      version.parse('a:1.2.3')
    with self.assertRaises(RuntimeError) as context:
      version.parse('1.2.3-')
    with self.assertRaises(RuntimeError) as context:
      version.parse('1.2.3-a')
    with self.assertRaises(RuntimeError) as context:
      version.parse('1:2:3')

  def test_cmp(self):
    self.assertEqual( -1, self.__cmp('1.2.3', '1.2.4') )
    self.assertEqual( 0, self.__cmp('1.2.3', '1.2.3') )
    self.assertEqual( 1, self.__cmp('1.2.4', '1.2.3') )
    
    self.assertEqual( 1, self.__cmp('1:1.2.3', '1.2.4') )
    self.assertEqual( -1, self.__cmp('0:1.2.3', '1.2.4') )
    self.assertEqual( -1, self.__cmp('0:1.2.3', '0:1.2.3-1') )
    self.assertEqual( 1, self.__cmp('0:1.2.3-3', '0:1.2.3-2') )

  def __cmp(self, v1, v2):
    return version.cmp(version.parse(v1), version.parse(v2))

if __name__ == "__main__":
  unit_test.main()

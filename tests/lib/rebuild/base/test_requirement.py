#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base.requirement import requirement as R

class test_requirement(unit_test):

  def test___str__(self):
    self.assertEqual( 'foo >= 1.2.3', str(R('foo', '>=', '1.2.3')) )
    self.assertEqual( 'orange >= 6.6.6', str(R('orange', '>=', '6.6.6')) )

  def test___str__with_system(self):
    self.assertEqual( 'foo(linux) >= 1.2.3', str(R('foo', '>=', '1.2.3', 'linux')) )
    self.assertEqual( 'orange >= 6.6.6', str(R('orange', '>=', '6.6.6', 'all')) )

  def test_to_string_colon_format(self):
    self.assertEqual( 'all: foo >= 1.2.3', R('foo', '>=', '1.2.3', None).to_string_colon_format() )
    self.assertEqual( 'linux: foo >= 1.2.3', R('foo', '>=', '1.2.3', 'linux').to_string_colon_format() )

  def test_to_string_colon_format_with_hardness(self):
    self.assertEqual( 'all: RUN foo >= 1.2.3', R('foo', '>=', '1.2.3', None, 'RUN').to_string_colon_format() )
    self.assertEqual( 'linux: TOOL foo >= 1.2.3', R('foo', '>=', '1.2.3', 'linux', 'TOOL').to_string_colon_format() )
    
  def test_to_string_colon_format_with_expression(self):
    self.assertEqual( 'all(${FOO} < 99): RUN foo >= 1.2.3', R('foo', '>=', '1.2.3', None, 'RUN', '${FOO} < 99').to_string_colon_format() )

  def test___str__with_hardness(self):
    self.assertEqual( 'RUN foo(linux) >= 1.2.3', str(R('foo', '>=', '1.2.3', 'linux', 'RUN')) )
    #self.assertEqual( 'orange >= 6.6.6', str(R('orange', '>=', '6.6.6', 'all', 'RUN')) )
    
  def test_clone_replace_hardness(self):
    r1 = R('foo', '>=', '1.2.3', 'linux', 'RUN')
    r2 = r1.clone_replace_hardness('BUILD')
    self.assertEqual( 'RUN', str(r1.hardness) )
    self.assertEqual( 'BUILD', str(r2.hardness) )
    
  def test_clone_replace_system_mask(self):
    r1 = R('foo', '>=', '1.2.3', 'linux', 'RUN')
    r2 = r1.clone_replace_system_mask('macos')
    self.assertEqual( 'linux', str(r1.system_mask) )
    self.assertEqual( 'macos', str(r2.system_mask) )
    
  def test_hardness_matches(self):
    self.assertTrue( R('foo', '>=', '1.2.3', 'linux', 'RUN').hardness_matches('RUN') )
    self.assertFalse( R('foo', '>=', '1.2.3', 'linux', 'RUN').hardness_matches('TOOL') )
    self.assertTrue( R('foo', '>=', '1.2.3', 'linux', None).hardness_matches('RUN') )
    
  def test_hardness_matches_seq(self):
    self.assertTrue( R('foo', '>=', '1.2.3', 'linux', 'RUN').hardness_matches([ 'RUN', 'TOOL']) )
    self.assertTrue( R('foo', '>=', '1.2.3', 'linux', 'TOOL').hardness_matches([ 'RUN', 'TOOL']) )
    self.assertTrue( R('foo', '>=', '1.2.3', 'linux', None).hardness_matches([ 'RUN', 'TOOL']) )
    
  def test_system_mask_matches(self):
    self.assertTrue( R('foo', '>=', '1.2.3', 'linux', None).system_mask_matches('linux') )
    self.assertFalse( R('foo', '>=', '1.2.3', 'linux', None).system_mask_matches('macos') )
    self.assertTrue( R('foo', '>=', '1.2.3', 'all', None).system_mask_matches('linux') )
    self.assertTrue( R('foo', '>=', '1.2.3', 'all', None).system_mask_matches('macos') )

if __name__ == "__main__":
  unit_test.main()

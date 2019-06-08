#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base.package_descriptor import package_descriptor as PD
from rebuild.base.package_descriptor_list import package_descriptor_list as PDL
from rebuild.base.requirement_list import requirement_list as RL

class test_package_descriptor_list(unit_test):

  def test___str__(self):
    l = PDL([
      PD('foo', '1.2.3-1'),
      PD('bar', '4.5.6'),
      PD('baz', '7.8.9'),
    ])
    self.assertEqual( 'foo-1.2.3-1\nbar-4.5.6\nbaz-7.8.9', str(l) )
            
  def test_names(self):
    l = PDL([
      PD('foo', '1.2.3-1'),
      PD('bar', '4.5.6'),
      PD('baz', '7.8.9'),
    ])
    self.assertEqual( [ 'foo', 'bar', 'baz' ], l.names() )
            
  def test___eq__(self):
    l1 = PDL([
      PD('foo', '1.2.3-1'),
      PD('bar', '4.5.6'),
      PD('baz', '7.8.9'),
    ])
    l2 = PDL([
      PD('foo', '1.2.3-1'),
      PD('bar', '4.5.6'),
      PD('baz', '7.8.9'),
    ])
    self.assertEqual( l1, l2 )

  def test_filter_by_requirement(self):
    P = PD.parse
    l = PDL([
      P('foo-1.0.0'),
      P('foo-1.0.2'),
      P('foo-1.0.2-1'),
      P('foo-1.0.2-2'),
      P('foo-1.0.9'),
      P('foo-1.0.10'),
      P('foo-1.0.10-1'),
      P('foo-1.0.10-2'),
    ])
    self.assertEqual( [ P('foo-1.0.0') ], l.filter_by_requirement(RL.parse('foo == 1.0.0')[0]) )
    self.assertEqual( [ P('foo-1.0.0'), P('foo-1.0.2') ], l.filter_by_requirement(RL.parse('foo <= 1.0.2')[0]) )
    self.assertEqual( [ P('foo-1.0.0'), P('foo-1.0.2'), P('foo-1.0.2-1') ], l.filter_by_requirement(RL.parse('foo <= 1.0.2-1')[0]) )
    self.assertEqual( [ P('foo-1.0.0'), P('foo-1.0.2'), P('foo-1.0.2-1') ], l.filter_by_requirement(RL.parse('foo <= 1.0.2-1')[0]) )
    
  def test_latest_versions(self):
    P = PD.parse
    l = PDL([
      P('foo-1.0.0'),
      P('foo-1.0.2'),
      P('foo-1.0.2-1'),
      P('bar-1.0.9'),
      P('bar-1.0.10'),
      P('baz-1.0.0'),
      P('baz-1.0.100'),
      P('baz-1.0.99'),
    ])
    expected = PDL([
      P('bar-1.0.10'),
      P('baz-1.0.100'),
      P('foo-1.0.2-1'),
    ])
    print('ACTUAL: %s\n' % (l.latest_versions().to_string()))
    self.assertMultiLineEqual( expected.to_string(), l.latest_versions().to_string() )
    
if __name__ == "__main__":
  unit_test.main()

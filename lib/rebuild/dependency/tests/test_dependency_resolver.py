#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest

from rebuild.dependency import dependency_resolver, cyclic_dependency_error, missing_dependency_error

class test_dependency_resolver(unittest.TestCase):

  def test_resolve_deps(self):
    dep_map = {
      'foo': set(),
      'bar': set(),
      'kiwi': set( [ 'foo' ] ),
      'cheese': set( [ 'kiwi', 'bar' ] ),
    }
    self.assertEqual( [ 'foo' ], dependency_resolver.resolve_deps(dep_map, 'foo') )
    self.assertEqual( [ 'bar' ], dependency_resolver.resolve_deps(dep_map, 'bar') )
    self.assertEqual( [ 'foo', 'kiwi' ], dependency_resolver.resolve_deps(dep_map, [ 'foo', 'kiwi' ]) )
    self.assertEqual( [ 'foo' ], dependency_resolver.resolve_deps(dep_map, [ 'foo', 'foo' ]) )

  def test_resolve_deps_cyclic(self):
    cycle_dep_map = {
      'c1': set( [ 'c2' ] ),
      'c2': set( [ 'c1' ] ),
      'c3': set( [ 'c4' ] ),
      'c4': set( [ 'c3' ] ),
      'f1': set( [ 'f2' ] ),
      'f2': set( [ 'f3' ] ),
      'f3': set( [ 'f1' ] ),
      'n1': set( [] ),
      'n2': set( [ 'n1' ] ),
    }
    with self.assertRaises(cyclic_dependency_error) as context:
      dependency_resolver.resolve_deps(cycle_dep_map, [ 'c1' ])
    self.assertEquals( [ 'c1', 'c2', 'c3', 'c4', 'f1', 'f2', 'f3' ], context.exception.cyclic_deps )

  def test_resolve_deps_missing(self):
    missing_dep_map = {
      'c1': set( [ 'x1' ] ),
      'c2': set( [ 'x2' ] ),
    }
    with self.assertRaises(missing_dependency_error) as context:
      dependency_resolver.resolve_deps(missing_dep_map, [ 'c1' ])
    self.assertEquals( [ 'x1' ], context.exception.missing_deps )

  def test_is_cyclic(self):
    cycle_dep_map = {
      'c1': set( [ 'c2' ] ),
      'c2': set( [ 'c1' ] ),
      'c3': set( [ 'c4' ] ),
      'c4': set( [ 'c3' ] ),
      'f1': set( [ 'f2' ] ),
      'f2': set( [ 'f3' ] ),
      'f3': set( [ 'f1' ] ),
    }
    no_cycle_dep_map = {
      'f1': set( [ 'f3' ] ),
      'f2': set( [ 'f3' ] ),
    }
    self.assertEqual( True, dependency_resolver.is_cyclic(cycle_dep_map) )
    self.assertEqual( False, dependency_resolver.is_cyclic(no_cycle_dep_map) )

  def test_cyclic_deps(self):
    cycle_dep_map = {
      'c1': set( [ 'c2' ] ),
      'c2': set( [ 'c1' ] ),
      'c3': set( [ 'c4' ] ),
      'c4': set( [ 'c3' ] ),
      'f1': set( [ 'f2' ] ),
      'f2': set( [ 'f3' ] ),
      'f3': set( [ 'f1' ] ),
    }
    self.assertEqual( [ 'c1', 'c2', 'c3', 'c4', 'f1', 'f2', 'f3' ], dependency_resolver.cyclic_deps(cycle_dep_map) )

  def test_check_missing(self):
    available = [
      'd1',
      'd2',
      'd3',
    ]
    self.assertEqual( [], dependency_resolver.check_missing(available, [ 'd1' ]) )
    self.assertEqual( [], dependency_resolver.check_missing(available, [ 'd1', 'd2', 'd3' ]) )
    self.assertEqual( [ 'n1' ], dependency_resolver.check_missing(available, [ 'd1', 'd2', 'd3', 'n1' ]) )
    self.assertEqual( [ 'n1' ], dependency_resolver.check_missing(available, [ 'n1' ]) )
    self.assertEqual( [ 'n1', 'n2' ], dependency_resolver.check_missing(available, [ 'd1', 'd2', 'd3', 'n1', 'n2' ]) )
    self.assertEqual( [ 'n1', 'n2' ], dependency_resolver.check_missing(available, [ 'n1', 'n2' ]) )

if __name__ == '__main__':
  unittest.main()

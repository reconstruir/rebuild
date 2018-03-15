#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import requirement as R, requirement_list as RL

class test_requirement_list(unit_test):

  def test_parse_dups(self):
    text = 'foo >= 1.2.3 orange >= 6.6.6 bar baz bar orange >= 6.6.6'
    requirements = RL.parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', None ),
      ( 'orange', '>=', '6.6.6', None ),
      ( 'bar', None, None, None ),
      ( 'baz', None, None, None ),
    ], requirements )
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', None ),
      ( 'orange', '>=', '6.6.6', None ),
      ( 'bar', None, None, None ),
      ( 'baz', None, None, None ),
    ], requirements )
  
  def test_to_string(self):
    reqs = RL([ R('foo', '>=', '1.2.3'), R('orange', '>=', '6.6.6'), R('bar', None, None), R('baz', None, None) ])
    self.assertEqual( 'foo >= 1.2.3 orange >= 6.6.6 bar baz', str(reqs) )

  def test_to_string_with_system(self):
    reqs = RL([ R('foo', '>=', '1.2.3', 'macos'), R('orange', '>=', '6.6.6', 'all'), R('bar', None, None, 'desktop'), R('baz', None, None, 'linux') ])
    self.assertEqual( 'foo(macos) >= 1.2.3 orange >= 6.6.6 bar(desktop) baz(linux)', str(reqs) )

  def test_resolve_requirements(self):
    text = 'apple(linux) >= 1.2.3 kiwi orange(macos) == 6.6.6 pear(ios) lychee(all) corn(desktop) tomato(linux|macos) <= 9.8.7'
    reqs = RL.parse(text)

    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', 'linux' ),
      ( 'kiwi', None, None, None ),
      ( 'lychee', None, None, 'all' ),
      ( 'corn', None, None, 'desktop' ),
      ( 'tomato', '<=', '9.8.7', 'linux|macos' ),
    ], reqs.resolve('linux') )

    self.assertEqual( [
      ( 'kiwi', None, None, None ),
      ( 'orange', '==', '6.6.6', 'macos' ),
      ( 'lychee', None, None, 'all' ),
      ( 'corn', None, None, 'desktop' ),
      ( 'tomato', '<=', '9.8.7', 'linux|macos' ),
    ], reqs.resolve('macos') )

    self.assertEqual( [
      ( 'kiwi', None, None, None ),
      ( 'pear', None, None, 'ios' ),
      ( 'lychee', None, None, 'all' ),
    ], reqs.resolve('ios') )

    self.assertEqual( [
      ( 'kiwi', None, None, None ),
      ( 'lychee', None, None, 'all' ),
    ], reqs.resolve('android') )

if __name__ == "__main__":
  unit_test.main()

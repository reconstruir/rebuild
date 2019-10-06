#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base.requirement import requirement as R
from rebuild.base.requirement_list import requirement_list as RL

class test_requirement_list(unit_test):

  def test_parse_dups(self):
    text = 'foo >= 1.2.3 orange >= 6.6.6 bar baz bar orange >= 6.6.6'
    requirements = RL.parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', None, None, None ),
      ( 'orange', '>=', '6.6.6', None, None, None ),
      ( 'bar', None, None, None, None, None ),
      ( 'baz', None, None, None, None, None ),
    ], requirements )
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', None, None, None ),
      ( 'orange', '>=', '6.6.6', None, None, None ),
      ( 'bar', None, None, None, None, None ),
      ( 'baz', None, None, None, None, None ),
    ], requirements )

  def test_parse_string_seq_list(self):
    text = [ 'foo >= 1.2.3', 'orange >= 6.6.6', 'bar', 'baz', 'bar', 'orange >= 6.6.6' ]
    requirements = RL.parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', None, None, None ),
      ( 'orange', '>=', '6.6.6', None, None, None ),
      ( 'bar', None, None, None, None, None ),
      ( 'baz', None, None, None, None, None ),
    ], requirements )
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', None, None, None ),
      ( 'orange', '>=', '6.6.6', None, None, None ),
      ( 'bar', None, None, None, None, None ),
      ( 'baz', None, None, None, None, None ),
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
      ( 'apple', '>=', '1.2.3', 'linux', None, None ),
      ( 'kiwi', None, None, None, None, None ),
      ( 'lychee', None, None, 'all', None, None ),
      ( 'corn', None, None, 'desktop', None, None ),
      ( 'tomato', '<=', '9.8.7', 'linux|macos', None, None ),
    ], reqs.resolve('linux') )

    self.assertEqual( [
      ( 'kiwi', None, None, None, None, None ),
      ( 'orange', '==', '6.6.6', 'macos', None, None ),
      ( 'lychee', None, None, 'all', None, None ),
      ( 'corn', None, None, 'desktop', None, None ),
      ( 'tomato', '<=', '9.8.7', 'linux|macos', None, None ),
    ], reqs.resolve('macos') )

    self.assertEqual( [
      ( 'kiwi', None, None, None, None, None ),
      ( 'pear', None, None, 'ios', None, None ),
      ( 'lychee', None, None, 'all', None, None ),
    ], reqs.resolve('ios') )

    self.assertEqual( [
      ( 'kiwi', None, None, None, None, None ),
      ( 'lychee', None, None, 'all', None, None ),
    ], reqs.resolve('android') )

  def test_filter_by_hardness(self):
    text = 'a >= 1.2 RUN b >= 2.3 TOOL c >= 3.4 BUILD d >= 5.6 e >= 6.7'
    r = RL.parse(text)
    self.assertEqual( [
      ( 'a', '>=', '1.2', None, None, None ),
      ( 'b', '>=', '2.3', None, 'RUN', None ),
      ( 'e', '>=', '6.7', None, None, None ),
    ], r.filter_by_hardness('RUN') )
    self.assertEqual( [
      ( 'c', '>=', '3.4', None, 'TOOL', None ),
    ], r.filter_by_hardness('TOOL') )
    self.assertEqual( [
      ( 'd', '>=', '5.6', None, 'BUILD', None ),
    ], r.filter_by_hardness('BUILD') )

  def test_filter_by_system(self):
    text = 'a(linux) >= 1.2 b(macos) >= 2.3 c(android) >= 3.4 d(desktop) >= 5.6 e(mobile) >= 6.7 f(ios) >= 7.8'
    r = RL.parse(text)
    self.assertEqual( [
      ( 'a', '>=', '1.2', 'linux', None, None ),
      ( 'd', '>=', '5.6', 'desktop', None, None ),
    ], r.filter_by_system('linux') )
    
  def test_names(self):
    r = RL.parse('a(linux) >= 1.2 b(macos) >= 2.3 c(android) >= 3.4 d(desktop) >= 5.6 e(mobile) >= 6.7 f(ios) >= 7.8')
    self.assertEqual( [ 'a', 'b', 'c', 'd', 'e', 'f' ], r.names(include_version = False) )
    self.assertEqual( [ 'a-1.2', 'b-2.3', 'c-3.4', 'd-5.6', 'e-6.7', 'f-7.8' ], r.names(include_version = True) )

  def test_dups(self):
    reqs = RL([ R('kiwi', None, None), R('orange', None, None), R('apple', None, None) ])
    self.assertEqual( [], reqs.dups() )
    
    reqs = RL([ R('kiwi', None, None), R('kiwi', None, None), R('orange', None, None), R('apple', None, None) ])
    self.assertEqual( [ 'kiwi' ], reqs.dups() )
    
if __name__ == "__main__":
  unit_test.main()

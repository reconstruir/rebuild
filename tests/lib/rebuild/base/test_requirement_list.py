#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import requirement as R, requirement_list as RL

class test_requirement_list(unit_test):

  def test_parse_basic(self):
    text = 'apple >= 1.2.3 kiwi pear lychee bananna kiwi-foo orange >= 6.6.6 strawberry >= 1.9'
    requirements = RL.parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', None ),
      ( 'kiwi', None, None, None ),
      ( 'pear', None, None, None ),
      ( 'lychee', None, None, None ),
      ( 'bananna', None, None, None ),
      ( 'kiwi-foo', None, None, None ),
      ( 'orange', '>=', '6.6.6', None ),
      ( 'strawberry', '>=', '1.9', None ),
    ], requirements )

  def test_parse_white_space(self):
    text = '    apple    >=     1.2.3 kiwi    pear     '
    requirements = RL.parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', None ),
      ( 'kiwi', None, None, None ),
      ( 'pear', None, None, None ),
    ], requirements )

  def test_parse_crunched(self):
    text = 'apple'
    requirements = RL.parse(text)
    self.assertEqual( [
      ( 'apple', None, None, None ),
    ], requirements )

  def test_parse_empty(self):
    text = ''
    requirements = RL.parse(text)
    self.assertEqual( [], requirements )

  def test_parse_single(self):
    text = ' apple'
    requirements = RL.parse(text)
    self.assertEqual( [
      ( 'apple', None, None, None ),
    ], requirements )

  def test_parse_single_versioned(self):
    text = 'apple >= 1.2.3'
    requirements = RL.parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', None ),
    ], requirements )

  def test_parse_operators(self):
    text = 'a > 1 b >= 1 c < 1 d <= 1 e == 1 f != 1'
    requirements = RL.parse(text)
    self.assertEqual( [
      ( 'a', '>', '1', None ),
      ( 'b', '>=', '1', None ),
      ( 'c', '<', '1', None ),
      ( 'd', '<=', '1', None ),
      ( 'e', '==', '1', None ),
      ( 'f', '!=', '1', None ),
    ], requirements )

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

  def test_parse_simple(self):
    text = 'foo >= 1.2.3'
    requirements = RL.parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', None ),
    ], requirements )

  def test_parse_multiple(self):
    text = 'foo >= 1.2.3 bar >= 6.6.6'
    requirements = RL.parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', None ),
      ( 'bar', '>=', '6.6.6', None ),
    ], requirements )

  def test_parse_requirement_with_system(self):
    self.maxDiff = None
    text = 'apple(linux) >= 1.2.3 kiwi orange(macos) == 6.6.6 pear(ios) lychee(all) corn(desktop) tomato(linux|macos) <= 9.8.7'
    requirements = RL.parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', 'linux' ),
      ( 'kiwi', None, None, None ),
      ( 'orange', '==', '6.6.6', 'macos' ),
      ( 'pear', None, None, 'ios' ),
      ( 'lychee', None, None, 'all' ),
      ( 'corn', None, None, 'desktop' ),
      ( 'tomato', '<=', '9.8.7', 'linux|macos' ),
    ], requirements )

  def test_parse_global_system_mask(self):
    text = 'all: foo >= 1.2.3'
    requirements = RL.parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', 'all' ),
    ], requirements )

  def test_parse_global_system_mask_and_override(self):
    text = 'all: foo(linux) >= 1.2.3'
    requirements = RL.parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', 'linux' ),
    ], requirements )
    
  def test_parse_with_comment(self):
    text = 'all: #foo >= 1.2.3'
    requirements = RL.parse(text)
    self.assertEqual( [], requirements )

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

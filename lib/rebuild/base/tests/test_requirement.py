#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from rebuild.base import requirement as R

class test_requirement(unit_test):

  def test_requirement(self):
    text = 'apple >= 1.2.3 kiwi pear lychee bananna kiwi-foo orange >= 6.6.6 strawberry >= 1.9'
    requirements = R.parse(text)
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

  def test_white_space(self):
    text = '    apple    >=     1.2.3 kiwi    pear     '
    requirements = R.parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', None ),
      ( 'kiwi', None, None, None ),
      ( 'pear', None, None, None ),
    ], requirements )

  def test_crunched(self):
    text = 'apple'
    requirements = R.parse(text)
    self.assertEqual( [
      ( 'apple', None, None, None ),
    ], requirements )

  def test_empty(self):
    text = ''
    requirements = R.parse(text)
    self.assertEqual( [], requirements )

  def test_single(self):
    text = ' apple'
    requirements = R.parse(text)
    self.assertEqual( [
      ( 'apple', None, None, None ),
    ], requirements )

  def test_single_versioned(self):
    text = 'apple >= 1.2.3'
    requirements = R.parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', None ),
    ], requirements )

  def test_operators(self):
    text = 'a > 1 b >= 1 c < 1 d <= 1 e == 1 f != 1'
    requirements = R.parse(text)
    self.assertEqual( [
      ( 'a', '>', '1', None ),
      ( 'b', '>=', '1', None ),
      ( 'c', '<', '1', None ),
      ( 'd', '<=', '1', None ),
      ( 'e', '==', '1', None ),
      ( 'f', '!=', '1', None ),
    ], requirements )

  def test_dups(self):
    text = 'foo >= 1.2.3 orange >= 6.6.6 bar baz bar orange >= 6.6.6'
    requirements = R.parse(text)
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

  def test___str__(self):
    reqs = R.parse('foo >= 1.2.3 orange >= 6.6.6')
    self.assertEqual( 'foo >= 1.2.3', str(reqs[0]) )
    self.assertEqual( 'orange >= 6.6.6', str(reqs[1]) )

  def test___str__with_system(self):
    reqs = R.parse('foo(linux) >= 1.2.3 orange(all) >= 6.6.6')
    self.assertEqual( 'foo(linux) >= 1.2.3', str(reqs[0]) )
    self.assertEqual( 'orange >= 6.6.6', str(reqs[1]) )

  def test_requirement_list_to_string(self):
    text = 'foo >= 1.2.3 orange >= 6.6.6 bar baz bar orange >= 6.6.6'
    reqs = R.parse(text)
    self.assertEqual( 'foo >= 1.2.3 orange >= 6.6.6 bar baz', R.requirement_list_to_string(reqs) )

  def test_to_string_colon_format(self):
    self.assertEqual( 'all: foo >= 1.2.3', R('foo', '>=', '1.2.3', None).to_string_colon_format() )
    
  def test_requirement_list_to_string_with_system(self):
    text = 'foo >= 1.2.3 orange(all) >= 6.6.6 baz(desktop) bar(linux)'
    reqs = R.parse(text)
    self.assertEqual( 'foo >= 1.2.3 orange >= 6.6.6 baz(desktop) bar(linux)', R.requirement_list_to_string(reqs) )
    
  def test_parse_simple(self):
    text = 'foo >= 1.2.3'
    requirements = R.parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', None ),
    ], requirements )

  def test_parse_multiple(self):
    text = 'foo >= 1.2.3 bar >= 6.6.6'
    requirements = R.parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', None ),
      ( 'bar', '>=', '6.6.6', None ),
    ], requirements )

  def test_requirement_with_system(self):
    self.maxDiff = None
    text = 'apple(linux) >= 1.2.3 kiwi orange(macos) == 6.6.6 pear(ios) lychee(all) corn(desktop) tomato(linux|macos) <= 9.8.7'
    requirements = R.parse(text)
    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', 'linux' ),
      ( 'kiwi', None, None, None ),
      ( 'orange', '==', '6.6.6', 'macos' ),
      ( 'pear', None, None, 'ios' ),
      ( 'lychee', None, None, 'all' ),
      ( 'corn', None, None, 'desktop' ),
      ( 'tomato', '<=', '9.8.7', 'linux|macos' ),
    ], requirements )

  def test_resolve_requirements(self):
    text = 'apple(linux) >= 1.2.3 kiwi orange(macos) == 6.6.6 pear(ios) lychee(all) corn(desktop) tomato(linux|macos) <= 9.8.7'
    requirements = R.parse(text)

    self.assertEqual( [
      ( 'apple', '>=', '1.2.3', 'linux' ),
      ( 'kiwi', None, None, None ),
      ( 'lychee', None, None, 'all' ),
      ( 'corn', None, None, 'desktop' ),
      ( 'tomato', '<=', '9.8.7', 'linux|macos' ),
    ], R.resolve_requirements(requirements, 'linux') )

    self.assertEqual( [
      ( 'kiwi', None, None, None ),
      ( 'orange', '==', '6.6.6', 'macos' ),
      ( 'lychee', None, None, 'all' ),
      ( 'corn', None, None, 'desktop' ),
      ( 'tomato', '<=', '9.8.7', 'linux|macos' ),
    ], R.resolve_requirements(requirements, 'macos') )

    self.assertEqual( [
      ( 'kiwi', None, None, None ),
      ( 'pear', None, None, 'ios' ),
      ( 'lychee', None, None, 'all' ),
    ], R.resolve_requirements(requirements, 'ios') )

    self.assertEqual( [
      ( 'kiwi', None, None, None ),
      ( 'lychee', None, None, 'all' ),
    ], R.resolve_requirements(requirements, 'android') )

  def test_parse_global_system_mask(self):
    text = 'all: foo >= 1.2.3'
    requirements = R.parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', 'all' ),
    ], requirements )

  def test_parse_global_system_mask_and_override(self):
    text = 'all: foo(linux) >= 1.2.3'
    requirements = R.parse(text)
    self.assertEqual( [
      ( 'foo', '>=', '1.2.3', 'linux' ),
    ], requirements )
    
if __name__ == "__main__":
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.base import requirement as R, requirement_list as RL

class test_requirement_list(unit_test):

  def test_to_string(self):
    reqs = RL([ R('foo', '>=', '1.2.3'), R('orange', '>=', '6.6.6'), R('bar', None, None), R('baz', None, None) ])
    self.assertEqual( 'foo >= 1.2.3 orange >= 6.6.6 bar baz', str(reqs) )

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
    
if __name__ == "__main__":
  unit_test.main()

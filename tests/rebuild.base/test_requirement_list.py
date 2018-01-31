#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from rebuild.base import requirement as R, requirement_list as RL

class test_requirement_list(unit_test):

  def test_to_string(self):
    reqs = RL([ R('foo', '>=', '1.2.3'), R('orange', '>=', '6.6.6'), R('bar', None, None), R('baz', None, None) ])
    self.assertEqual( 'foo >= 1.2.3 orange >= 6.6.6 bar baz', str(reqs) )

  def xtest_to_string_with_system(self):
    text = 'foo >= 1.2.3 orange(all) >= 6.6.6 baz(desktop) bar(linux)'
    reqs = R.parse(text)
    self.assertEqual( 'foo >= 1.2.3 orange >= 6.6.6 baz(desktop) bar(linux)', R.requirement_list_to_string(reqs) )

if __name__ == "__main__":
  unit_test.main()

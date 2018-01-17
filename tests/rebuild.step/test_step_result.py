#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import unittest
from rebuild.step import step_result

class Teststep_result(unittest.TestCase):

  def test_tag(self):
    r = step_result(True, 'foo', None)
    self.assertEqual( True, r.success )
    self.assertEqual( 'foo', r.message )
    self.assertEqual( None, r.failed_step )

if __name__ == '__main__':
  unittest.main()

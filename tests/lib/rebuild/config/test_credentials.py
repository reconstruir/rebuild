#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.testing.unit_test import unit_test
from rebuild.config import credentials

class test_credentials(unit_test):

  def test_basic(self):
    c = credentials('fred', 'flintpass')
    self.assertEqual( 'fred', c.username )
    self.assertEqual( 'flintpass', c.password )
    
  def test_env_vars(self):
    c = credentials('${MY_USERNAME}', '${MY_PASSWORD}')
    try:
      os.environ['MY_USERNAME'] = 'fred'
      os.environ['MY_PASSWORD'] = 'flintpass'
      self.assertEqual( 'fred', c.username )
      self.assertEqual( 'flintpass', c.password )
    finally:
      del os.environ['MY_USERNAME']
      del os.environ['MY_PASSWORD']

if __name__ == '__main__':
  unit_test.main()

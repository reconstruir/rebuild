#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.testing.unit_test import unit_test
from rebuild.config import credentials
from bes.system.env_override import env_override

class test_credentials(unit_test):

  def test_basic(self):
    c = credentials('fred', 'flintpass')
    self.assertEqual( 'fred', c.username )
    self.assertEqual( 'flintpass', c.password )
    
  def test_env_vars(self):
    c = credentials('${MY_USERNAME}', '${MY_PASSWORD}')
    with env_override( { 'MY_USERNAME': 'fred', 'MY_PASSWORD': 'flintpass' }) as env:
      self.assertEqual( 'fred', c.username )
      self.assertEqual( 'flintpass', c.password )

if __name__ == '__main__':
  unit_test.main()

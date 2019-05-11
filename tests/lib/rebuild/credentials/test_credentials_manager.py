#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.testing.unit_test import unit_test
from rebuild.credentials.credentials_manager import credentials_manager
from rebuild.credentials.credentials_source_aws import credentials_source_aws
from rebuild.credentials.credentials_source_env import credentials_source_env
from rebuild.gradle.credentials_source_gradle import credentials_source_gradle
from bes.system.env_override import env_override

class test_credentials_manager(unit_test):

  def test_basic(self):
    cm = credentials_manager()
    #c.username = 'fred'
    #c.password = 'flintpass'
    #self.assertEqual( 'fred', c.username )
    #self.assertEqual( 'flintpass', c.password )
    
  def xtest_env_vars(self):
    c = credentials()
    c.username = '${MY_USERNAME}'
    c.password = '${MY_PASSWORD}'
    with env_override( { 'MY_USERNAME': 'fred', 'MY_PASSWORD': 'flintpass' }) as env:
      self.assertEqual( 'fred', c.username )
      self.assertEqual( 'flintpass', c.password )

if __name__ == '__main__':
  unit_test.main()

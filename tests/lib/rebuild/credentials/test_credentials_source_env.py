#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.testing.unit_test import unit_test
from rebuild.credentials.credentials_source_env import credentials_source_env as CSE
from bes.system.env_override import env_override
from bes.fs.temp_file import temp_file

class test_credentials_source_env(unit_test):

  def test_valid(self):
    cs = CSE({ 'username': '${MY_USERNAME}', 'password': '${MY_PASSWORD}' })
    with env_override( { 'MY_USERNAME': 'fred', 'MY_PASSWORD': 'flintpass' }) as env:
      self.assertEqual( True, cs.is_valid() )
      c = cs.credentials()
      self.assertEqual( 'fred', c.username )
      self.assertEqual( 'flintpass', c.password )

  def test_invalid(self):
    cs = CSE({ 'username': '${MY_USERNAME}', 'password': '${MY_PASSWORD}' })
    with env_override( { 'MY_USERNAME': 'fred' }) as env:
      self.assertEqual( False, cs.is_valid() )

if __name__ == '__main__':
  unit_test.main()

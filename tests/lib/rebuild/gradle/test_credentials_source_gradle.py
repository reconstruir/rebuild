#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.testing.unit_test import unit_test
from rebuild.gradle.credentials_source_gradle import credentials_source_gradle as CSG
from bes.system.env_override import env_override
from bes.fs import temp_file

class test_credentials_source_gradle(unit_test):

  def test_valid(self):
    text = '''\
devUser=fred@flintstone.com
devPassword=flintpass
systemProp.gradle.wrapperUser=tuser
systemProp.gradle.wrapperPassword=tpassword
'''
    cs = CSG(temp_file.make_temp_file(content = text), 'dev')
    self.assertEqual( True, cs.is_valid() )
    c = cs.credentials()
    self.assertEqual( 'fred@flintstone.com', c.user )
    self.assertEqual( 'flintpass', c.password )
    
  def test_invalid(self):
    text = 'notvalid'
    cs = CSG(temp_file.make_temp_file(content = text), 'dev')
    self.assertEqual( False, cs.is_valid() )
    c = cs.credentials()
    

if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.config.storage_config import storage_config as SC
from rebuild.config.credentials import credentials

class test_storage_config(unit_test):
    
  def test_fullpath(self):
    cred = credentials('fred', 'flintpass')
    self.assertEqual( '/myloc/myrepo/myroot', SC('foo', 'local', '/myloc', 'myrepo', 'myroot', cred, cred).full_path )
    self.assertEqual( '/myloc/myroot', SC('foo', 'local', '/myloc', None, 'myroot', cred, cred).full_path )
    self.assertEqual( '/myloc/myrepo', SC('foo', 'local', '/myloc', 'myrepo', None, cred, cred).full_path )
    
if __name__ == '__main__':
  unit_test.main()

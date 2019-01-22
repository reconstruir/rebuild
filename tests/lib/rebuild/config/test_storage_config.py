#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
from bes.testing.unit_test import unit_test
from rebuild.config.storage_config import storage_config as SC
from rebuild.config.credentials import credentials

class test_storage_config(unit_test):
    
  def test_fullpath(self):
    cred = credentials('fred', 'flintpass')
    self.assertEqual( '/myloc/myrepo/myroot', SC('foo', 'local', '/myloc', 'myrepo', 'myroot', cred, cred).full_path )
    self.assertEqual( '/myloc/myroot', SC('foo', 'local', '/myloc', None, 'myroot', cred, cred).full_path )
    self.assertEqual( '/myloc/myrepo', SC('foo', 'local', '/myloc', 'myrepo', None, cred, cred).full_path )
    
  def test_env_vars(self):
    dcred = credentials('${MY_DOWNLOAD_USERNAME}', '${MY_DOWNLOAD_PASSWORD}')
    ucred = credentials('${MY_UPLOAD_USERNAME}', '${MY_UPLOAD_PASSWORD}')
    try:
      os.environ['MY_DOWNLOAD_USERNAME'] = 'fred'
      os.environ['MY_DOWNLOAD_PASSWORD'] = 'flintpass'
      os.environ['MY_UPLOAD_USERNAME'] = 'ufred'
      os.environ['MY_UPLOAD_PASSWORD'] = 'uflintpass'
      os.environ['MY_PROVIDER'] = 'local'
      os.environ['MY_LOCATION'] = '/myloc'
      os.environ['MY_REPO'] = 'myrepo'
      os.environ['MY_ROOT'] = 'myroot'
      c = SC('foo', '${MY_PROVIDER}', '${MY_LOCATION}', '${MY_REPO}', '${MY_ROOT}', dcred, ucred)
      self.assertEqual( '/myloc/myrepo/myroot', c.full_path )
      self.assertEqual( 'ufred', c.upload.username )
      self.assertEqual( 'uflintpass', c.upload.password )
      self.assertEqual( 'fred', c.download.username )
      self.assertEqual( 'flintpass', c.download.password )
      self.assertEqual( '/myloc/myroot', SC('foo', '${MY_PROVIDER}', '${MY_LOCATION}', None, '${MY_ROOT}', dcred, ucred).full_path )
      self.assertEqual( '/myloc/myrepo', SC('foo', '${MY_PROVIDER}', '${MY_LOCATION}', '${MY_REPO}', None, dcred, ucred).full_path )
    finally:
      for key in [ 'MY_DOWNLOAD_USERNAME', 'MY_DOWNLOAD_PASSWORD', 'MY_UPLOAD_USERNAME', 'MY_UPLOAD_PASSWORD', 'MY_PROVIDER', 'MY_LOCATION', 'MY_REPO', 'MY_ROOT' ]:
        del os.environ[key]

  def test_expanduser(self):
    cred = credentials('fred', 'flintpass')
    self.assertEqual( path.expanduser('~/myloc/myrepo/myroot'), SC('foo', 'local', '~/myloc', 'myrepo', 'myroot', cred, cred).full_path )
        
if __name__ == '__main__':
  unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
from bes.testing.unit_test import unit_test
from bes.system.env_override import env_override

from rebuild.config.storage_config import storage_config as SC
from rebuild.credentials.credentials import credentials

class test_storage_config(unit_test):
    
  def test_fullpath(self):
    cred = credentials('<unittest>', username = 'fred', password = 'flintpass')
    self.assertEqual( '/myloc/myrepo/myroot', SC('foo', 'local', '/myloc', 'myrepo', 'myroot', cred, cred).full_path )
    self.assertEqual( '/myloc/myroot', SC('foo', 'local', '/myloc', None, 'myroot', cred, cred).full_path )
    self.assertEqual( '/myloc/myrepo', SC('foo', 'local', '/myloc', 'myrepo', None, cred, cred).full_path )
    
  def test_env_vars(self):
    dcred = credentials('<unittest>', username = '${MY_DOWNLOAD_USERNAME}', password = '${MY_DOWNLOAD_PASSWORD}')
    ucred = credentials('<unittest>', username = '${MY_UPLOAD_USERNAME}', password = '${MY_UPLOAD_PASSWORD}')
    with env_override( {
        'MY_DOWNLOAD_USERNAME': 'fred',
        'MY_DOWNLOAD_PASSWORD': 'flintpass',
        'MY_UPLOAD_USERNAME': 'ufred',
        'MY_UPLOAD_PASSWORD': 'uflintpass',
        'MY_PROVIDER': 'local',
        'MY_LOCATION': '/myloc',
        'MY_REPO': 'myrepo',
        'MY_ROOT': 'myroot',
    }) as env:
      c = SC('foo', '${MY_PROVIDER}', '${MY_LOCATION}', '${MY_REPO}', '${MY_ROOT}', dcred, ucred)
      self.assertEqual( '/myloc/myrepo/myroot', c.full_path )
      self.assertEqual( 'ufred', c.upload.username )
      self.assertEqual( 'uflintpass', c.upload.password )
      self.assertEqual( 'fred', c.download.username )
      self.assertEqual( 'flintpass', c.download.password )
      self.assertEqual( '/myloc/myroot', SC('foo', '${MY_PROVIDER}', '${MY_LOCATION}', None, '${MY_ROOT}', dcred, ucred).full_path )
      self.assertEqual( '/myloc/myrepo', SC('foo', '${MY_PROVIDER}', '${MY_LOCATION}', '${MY_REPO}', None, dcred, ucred).full_path )

  def test_expanduser(self):
    cred = credentials('<unittest>', username = 'fred', password = 'flintpass')
    self.assertEqual( path.expanduser('~/myloc/myrepo/myroot'), SC('foo', 'local', '~/myloc', 'myrepo', 'myroot', cred, cred).full_path )
        
if __name__ == '__main__':
  unit_test.main()

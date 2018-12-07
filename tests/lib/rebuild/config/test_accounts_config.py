#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.testing.unit_test import unit_test
from rebuild.config import accounts_config

class test_accounts_config(unit_test):
    
  def test_basic(self):
    text='''
credential
  provider: pcloud
  purpose: download
  email: download@bar.com
  password: sekret1

credential
  provider: pcloud
  purpose: upload
  email: upload@bar.com
  password: sekret2

account
  name: mine_pcloud
  description: mine personal pcloud account
  purpose: artifacts sources
  provider: pcloud
  root_dir: /mydir
'''
    ac = accounts_config(text, '<test>')
    #import pprint
    #print(pprint.pformat(ac._accounts))
    a = ac.find('artifacts', 'mine_pcloud')
    self.assertEqual( {
      'email': 'download@bar.com',
      'password': 'sekret1',
      'root_dir': '/mydir',
    }, a.download_values )
    self.assertEqual( {
      'email': 'upload@bar.com',
      'password': 'sekret2',
      'root_dir': '/mydir',
    }, a.upload_values )
    
if __name__ == '__main__':
  unit_test.main()

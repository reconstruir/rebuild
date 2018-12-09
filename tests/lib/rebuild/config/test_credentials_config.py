#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.config import credentials_config as CM

class test_credentials_config(unit_test):

  def test_separate(self):
    text = '''\
credential
  provider: pcloud
  purpose: download
  username: foo1@bar.com
  password: sekret1

credential
  provider: pcloud
  purpose: upload
  username: foo2@bar.com
  password: sekret2
'''
    cm = CM(text, '<test>')
    c = cm.get('download', 'pcloud')
    self.assertEqual( 'foo1@bar.com', c.username )
    self.assertEqual( 'sekret1', c.password )

    c = cm.get('upload', 'pcloud')
    self.assertEqual( 'foo2@bar.com', c.username )
    self.assertEqual( 'sekret2', c.password )
    
  def test_combined(self):
    text = '''\
credential
  provider: pcloud
  purpose: upload download
  username: foo@bar.com
  password: sekret
'''
    cm = CM(text, '<test>')
    c = cm.get('download', 'pcloud')
    self.assertEqual( 'foo@bar.com', c.username )
    self.assertEqual( 'sekret', c.password )

    c = cm.get('upload', 'pcloud')
    self.assertEqual( 'foo@bar.com', c.username )
    self.assertEqual( 'sekret', c.password )
    
if __name__ == '__main__':
  unit_test.main()

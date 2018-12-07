#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.config import credentials_config as CM

class test_credentials_config(unit_test):

  def test_separate(self):
    text = '''\
credential
  provider: pcloud
  type: download
  email: foo1@bar.com
  password: sekret1

credential
  provider: pcloud
  type: upload
  email: foo2@bar.com
  password: sekret2
'''
    cm = CM(text, '<test>')
    c = cm.find('download', 'pcloud')
    self.assertEqual( {
      'email': 'foo1@bar.com',
      'password': 'sekret1',
    }, c.values )
    c = cm.find('upload', 'pcloud')
    self.assertEqual( {
      'email': 'foo2@bar.com',
      'password': 'sekret2',
    }, c.values )
    
  def test_combined(self):
    text = '''\
credential
  provider: pcloud
  type: upload download
  email: foo@bar.com
  password: sekret
'''
    cm = CM(text, '<test>')
    c = cm.find('download', 'pcloud')
    self.assertEqual( {
      'email': 'foo@bar.com',
      'password': 'sekret',
    }, c.values )
    c = cm.find('upload', 'pcloud')
    self.assertEqual( {
      'email': 'foo@bar.com',
      'password': 'sekret',
    }, c.values )
    
if __name__ == '__main__':
  unit_test.main()

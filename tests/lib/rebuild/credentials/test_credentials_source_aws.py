#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.testing.unit_test import unit_test
from rebuild.credentials.credentials_source_aws import credentials_source_aws as CSA
from bes.system.env_override import env_override
from bes.fs.temp_file import temp_file

class test_credentials_source_aws(unit_test):

  def test_valid(self):
    text = '''\
[default]
aws_access_key_id = ABCDEFGHIJKLMNOPQRST
aws_secret_access_key = abcdefghijklmnopqrtuvwxyz1234567890abcde
output = text
region = us-west-2
'''
    cs = CSA(filename = temp_file.make_temp_file(content = text))
    self.assertEqual( True, cs.is_valid() )
    c = cs.credentials()
    self.assertEqual( 'ABCDEFGHIJKLMNOPQRST', c.aws_access_key_id )
    self.assertEqual( 'abcdefghijklmnopqrtuvwxyz1234567890abcde', c.aws_secret_access_key )
    self.assertEqual( 'abcdefghijklmnopqrtuvwxyz1234567890abcde', c.aws_secret_access_key )
    self.assertEqual( 'text', c.output )
    self.assertEqual( 'us-west-2', c.region )
    
  def test_invalid(self):
    text = 'notvalid'
    cs = CSA(filename = temp_file.make_temp_file(content = text))
    self.assertEqual( False, cs.is_valid() )
    c = cs.credentials()
    

if __name__ == '__main__':
  unit_test.main()

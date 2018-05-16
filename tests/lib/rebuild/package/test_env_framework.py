#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import temp_file
from rebuild.package import env_framework

class test_env_framework(unit_test):

  def test_extract(self):
    tmp_dir = temp_file.make_temp_dir(delete = False)
    ef = env_framework()
    ef.extract(tmp_dir)
    print('tmp_dir: %s' % (tmp_dir))
    
if __name__ == '__main__':
  unit_test.main()

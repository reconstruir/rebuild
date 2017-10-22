#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.checksum import checksum_manager

class test_checksum_manager(unit_test):

  def test_ignored(self):
    pass

if __name__ == '__main__':
  unit_test.main()

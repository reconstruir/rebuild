#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.storage import storage_chain, storage_hard_coded

from test_storage_local import source_dir_maker

class test_storage_chain(unit_test):
  pass

if __name__ == '__main__':
  unit_test.main()

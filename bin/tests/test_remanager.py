#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import script_unit_test

class test_remanager(script_unit_test):

  __unit_test_data_dir__ = '../../lib/rebuild/test_data/remanager'
  __script__ = __file__, '../rebuild_manager.py'

  def test_update(self):
    #rebuild_manager.py packages update --artifacts ${HOME}/proj/third_party/BUILD/artifacts --root-dir ${HOME}/.rebuild ${1+"$@"}
    rv = self.run_script()
    print("rv: %s" % (str(rv)))

if __name__ == '__main__':
  script_unit_test.main()

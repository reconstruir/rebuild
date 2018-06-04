#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.package import artifact_descriptor as AD

class test_artifact_descriptor(unit_test):

  def test_parse_filename(self):
    f = AD.parse_artifact_filename

    self.assertEqual( ( 'gnu_libtool', '2.4.6', 0, 0, 'macos', 'release', [ 'x86_64' ], '' ),
                      f('macos/x86_64/release/gnu_libtool-2.4.6.tar.gz') )

    self.assertEqual( ( 'gnu_libtool', '2.4.6', 0, 0, 'macos', 'debug', [ 'x86_64' ], '' ),
                      f('macos/x86_64/debug/gnu_libtool-2.4.6.tar.gz') )

    self.assertEqual( ( 'gnu_libtool', '2.4.6', 0, 0, 'linux', 'release', [ 'x86_64' ], '' ),
                      f('linux/x86_64/release/gnu_libtool-2.4.6.tar.gz') )

    self.assertEqual( ( 'gnu_libtool', '2.4.6', 0, 0, 'linux', 'debug', [ 'x86_64' ], '' ),
                      f('linux/x86_64/debug/gnu_libtool-2.4.6.tar.gz') )


  def test_full_name(self):
    self.assertEqual( 'foo-1.2.3', AD('foo', '1.2.3', 0, 0, 'linux', 'debug', [ 'x86_64' ], '').full_name )
    self.assertEqual( 'foo-1.2.3-1', AD('foo', '1.2.3', 1, 0, 'linux', 'debug', [ 'x86_64' ], '').full_name )
    self.assertEqual( 'foo-1:1.2.3-1', AD('foo', '1.2.3', 1, 1, 'linux', 'debug', [ 'x86_64' ], '').full_name )
    
if __name__ == '__main__':
  unit_test.main()

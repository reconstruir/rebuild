#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from rebuild import PackageFlags

class test_PackageFlags(unittest.TestCase):

  def test_init(self):
    pf = PackageFlags(cpppath = 'a', libpath = 'b', shlinkflags = 'c', libs = 'd')
    self.assertEqual( [ 'a' ], pf.cpppath )
    self.assertEqual( [ 'b' ], pf.libpath )
    self.assertEqual( [ 'c' ], pf.shlinkflags )
    self.assertEqual( [ 'd' ], pf.libs )

  def test_add(self):
    pf1 = PackageFlags(cpppath = 'a', libpath = 'b', shlinkflags = 'c', libs = 'd')
    pf2 = PackageFlags(cpppath = 'e', libpath = 'f', shlinkflags = 'g', libs = 'h')

    pf3 = PackageFlags()
    pf3 += pf1
    pf3 += pf2

    self.assertEqual( [ 'a', 'e' ], pf3.cpppath )
    self.assertEqual( [ 'b', 'f' ], pf3.libpath )
    self.assertEqual( [ 'c', 'g' ], pf3.shlinkflags )
    self.assertEqual( [ 'd', 'h' ], pf3.libs )

    self.assertEqual( [ 'a' ], pf1.cpppath )
    self.assertEqual( [ 'b' ], pf1.libpath )
    self.assertEqual( [ 'c' ], pf1.shlinkflags )
    self.assertEqual( [ 'd' ], pf1.libs )

    self.assertEqual( [ 'e' ], pf2.cpppath )
    self.assertEqual( [ 'f' ], pf2.libpath )
    self.assertEqual( [ 'g' ], pf2.shlinkflags )
    self.assertEqual( [ 'h' ], pf2.libs )

  def test_to_scons_environment(self):
    pf = PackageFlags(cpppath = [ 'foo', 'bar' ], libpath = [], shlinkflags = [ 'almond', 'walnut' ], libs = [ 'dog', 'cat', 'goat' ])

    self.assertEqual( { 'CPPPATH': [ 'foo', 'bar' ],
                        'LIBPATH': [],
                        'SHLINKFLAGS': [ 'almond', 'walnut' ],
                        'LIBS': [ 'dog', 'cat', 'goat' ] },
                      pf.to_scons_environment() )
    
if __name__ == '__main__':
  unittest.main()

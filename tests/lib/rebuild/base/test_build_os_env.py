#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, unittest
from rebuild.base import build_os_env
from bes.system import host

class Testbuild_os_env(unittest.TestCase):

  def test_path_reset(self):
    build_os_env.path_reset()
    self.assertTrue( build_os_env.CLEAN_PATH_MAP[host.SYSTEM], build_os_env.PATH.path )

  def test_path_append_remove(self):
    build_os_env.PATH.cleanup()
    old_path = build_os_env.PATH.path
    build_os_env.PATH.append('FOO')
    build_os_env.PATH.remove('FOO')
    self.assertEqual( old_path, build_os_env.PATH.path )

  def test_key_is_path(self):
    self.assertTrue( build_os_env.key_is_path('PATH') )
    self.assertTrue( build_os_env.key_is_path('LD_LIBRARY_PATH') )
    self.assertFalse( build_os_env.key_is_path('USER') )

  def test_update_empty(self):
    env = {}
    d = { 'PATH': 'foo:bar' }
    self.assertEqual( { 'PATH': self._sep('foo:bar') }, build_os_env.clone_and_update(env, d) )
    self.assertEqual( { 'PATH': self._sep('foo:bar') }, build_os_env.clone_and_update(env, d, prepend = True) )

    self.assertEqual( {}, build_os_env.clone_and_update({}, {}) )

  def test_update(self):
    env = { 'PATH': 'baz:biz', 'USER': 'me' }
    d = { 'PATH': 'foo:bar' }
    self.assertEqual( { 'PATH': self._sep('baz:biz:foo:bar'), 'USER': 'me' }, build_os_env.clone_and_update(env, d) )
    self.assertEqual( { 'PATH': self._sep('foo:bar:baz:biz'), 'USER': 'me' }, build_os_env.clone_and_update(env, d, prepend = True) )

  def test_clone_and_update(self):
    env = { 'foo': 666, 'bar': 'hi' }
    d = { 'fruit': 'apple' }
    new_env = build_os_env.clone_and_update(env, d)
    #self.assertEqual( self._sep('foo:bar'), os_env_var.path_join([ 'foo', 'bar' ]) )
    #self.assertEqual( self._sep('foo:bar:foo'), os_env_var.path_join([ 'foo', 'bar', 'foo' ]) )
    #self.assertEqual( self._sep('foo:bar:bar'), os_env_var.path_join([ 'foo', 'bar', 'bar' ]) )

  @classmethod
  def _sep(clazz, s):
    return s.replace(':', os.pathsep)
  
if __name__ == '__main__':
  unittest.main()

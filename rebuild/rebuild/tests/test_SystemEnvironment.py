#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os, unittest
from rebuild import SystemEnvironment
from bes.system import host

class TestSystemEnvironment(unittest.TestCase):

  def test_path_reset(self):
    SystemEnvironment.path_reset()
    self.assertTrue( SystemEnvironment.CLEAN_PATH_MAP[host.SYSTEM], SystemEnvironment.PATH.path )

  def test_path_append_remove(self):
    SystemEnvironment.PATH.cleanup()
    old_path = SystemEnvironment.PATH.path
    SystemEnvironment.PATH.append('FOO')
    SystemEnvironment.PATH.remove('FOO')
    self.assertEqual( old_path, SystemEnvironment.PATH.path )

  def test_key_is_path(self):
    self.assertTrue( SystemEnvironment.key_is_path('PATH') )
    self.assertTrue( SystemEnvironment.key_is_path('LD_LIBRARY_PATH') )
    self.assertFalse( SystemEnvironment.key_is_path('USER') )

  def test_update_empty(self):
    env = {}
    d = { 'PATH': 'foo:bar' }
    self.assertEqual( { 'PATH': self._sep('foo:bar') }, SystemEnvironment.clone_and_update(env, d) )
    self.assertEqual( { 'PATH': self._sep('foo:bar') }, SystemEnvironment.clone_and_update(env, d, prepend = True) )

    self.assertEqual( {}, SystemEnvironment.clone_and_update({}, {}) )

  def test_update(self):
    env = { 'PATH': 'baz:biz', 'USER': 'me' }
    d = { 'PATH': 'foo:bar' }
    self.assertEqual( { 'PATH': self._sep('baz:biz:foo:bar'), 'USER': 'me' }, SystemEnvironment.clone_and_update(env, d) )
    self.assertEqual( { 'PATH': self._sep('foo:bar:baz:biz'), 'USER': 'me' }, SystemEnvironment.clone_and_update(env, d, prepend = True) )

  def test_clone_and_update(self):
    env = { 'foo': 666, 'bar': 'hi' }
    d = { 'fruit': 'apple' }
    new_env = SystemEnvironment.clone_and_update(env, d)
    #self.assertEqual( self._sep('foo:bar'), os_env_var.path_join([ 'foo', 'bar' ]) )
    #self.assertEqual( self._sep('foo:bar:foo'), os_env_var.path_join([ 'foo', 'bar', 'foo' ]) )
    #self.assertEqual( self._sep('foo:bar:bar'), os_env_var.path_join([ 'foo', 'bar', 'bar' ]) )

  @classmethod
  def _sep(clazz, s):
    return s.replace(':', os.pathsep)
  
if __name__ == '__main__':
  unittest.main()

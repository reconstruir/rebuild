#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from bes.key_value import key_value
from rebuild import platform_specific_config as psc
from rebuild import System

class test_platform_specific_config(unit_test):

  def test_simple(self):
    self.assertEqual( ( 'linux', 'foo bar baz' ), psc.parse('linux: foo bar baz') )

  def test_simple_white_space(self):
    self.assertEqual( ( 'linux', 'foo bar baz' ), psc.parse('linux:      foo bar baz     ') )

  def test_key_values(self):
    self.assertEqual( ( 'linux', [ ( 'foo', '5' ), ( 'bar', 'hi' ) ] ), psc.parse_key_values('linux: foo=5 bar=hi') )

  def test_key_values_with_spaces(self):
    self.assertEqual( ( 'linux', [ ( 'foo', '"1 2 3"' ), ( 'bar', "'a b c'" ) ] ), psc.parse_key_values('linux: foo="1 2 3" bar=\'a b c\'') )
    self.assertEqual( ( 'linux', [ ( 'foo', '"1 2 3"' ), ( 'bar', None ) ] ), psc.parse_key_values('linux: foo="1 2 3" bar=') )

  def test_parse_list(self):
    self.assertEqual( ( 'linux', [ '--foo', '--bar', 'BAZ="a b c"' ] ), psc.parse_list('linux: --foo --bar BAZ=\"a b c\"') )
    self.assertEqual( ( 'linux', [ 'foo="a b c"' ] ), psc.parse_list('linux: foo="a b c"') )
    self.assertEqual( ( 'linux', [ 'CFLAGS="-f foo -g bar"' ] ), psc.parse_list(r'linux: CFLAGS="-f foo -g bar"') )

  def test_resolve_key_values(self):
    config = [
      'all: foo=666 bar=hi',
      'linux: creator=linus',
      'macos: creator=steve',
      'android: creator=andy',
    ]
    self.assertEqual( [ key_value('foo', '666'), key_value('bar', 'hi'), key_value('creator', 'linus') ],
                      psc.resolve_key_values(config, 'linux') )
    self.assertEqual( [ key_value('foo', '666'), key_value('bar', 'hi'), key_value('creator', 'steve') ],
                      psc.resolve_key_values(config, 'macos') )
    self.assertEqual( [ key_value('foo', '666'), key_value('bar', 'hi'), key_value('creator', 'andy') ],
                      psc.resolve_key_values(config, 'android') )
                        
  def test_resolve_key_values_duplicate_keys(self):
    config = [
      'all: foo=666',
      'linux: creator=linus',
      'macos: creator=steve',
      'android: creator=andy',
      'linux|macos: creator=engineers',
    ]
    self.assertEqual( [ key_value('foo', '666'), key_value('creator', 'linus'), key_value('creator', 'engineers') ],
                      psc.resolve_key_values(config, 'linux') )
    self.assertEqual( [ key_value('foo', '666'), key_value('creator', 'steve'), key_value('creator', 'engineers') ],
                      psc.resolve_key_values(config, 'macos') )
    self.assertEqual( [ key_value('foo', '666'), key_value('creator', 'andy') ],
                      psc.resolve_key_values(config, 'android') )

  def test_resolve_key_values_to_dict(self):
    config = [
      'all: foo=666 bar=hi',
      'linux: creator=linus',
      'macos: creator=steve',
      'android: creator=andy',
    ]
    self.assertEqual( { 'foo': '666', 'bar': 'hi', 'creator': 'linus' },
                      psc.resolve_key_values_to_dict(config, 'linux') )
    self.assertEqual( { 'foo': '666', 'bar': 'hi', 'creator': 'steve' },
                      psc.resolve_key_values_to_dict(config, 'macos') )
    self.assertEqual( { 'foo': '666', 'bar': 'hi', 'creator': 'andy' },
                      psc.resolve_key_values_to_dict(config, 'android') )
                        
  def test_resolve_key_values_to_dict_duplicate_keys(self):
    config = [
      'all: foo=666',
      'linux: creator=linus',
      'macos: creator=steve',
      'android: creator=andy',
      'linux|macos: creator=engineers',
    ]
    self.assertEqual( { 'foo': '666', 'creator': 'engineers' },
                      psc.resolve_key_values_to_dict(config, 'linux') )
    self.assertEqual( { 'foo': '666', 'creator': 'engineers' },
                      psc.resolve_key_values_to_dict(config, 'macos') )
    self.assertEqual( { 'foo': '666', 'creator': 'andy' },
                      psc.resolve_key_values_to_dict(config, 'android') )
                        
  def test_resolve_list(self):
    config = [
      'all: --foo --bar',
      'linux: --linux',
      'macos: --macos',
      'android: --android',
    ]
    self.assertEqual( [ '--foo', '--bar', '--linux' ],
                      psc.resolve_list(config, 'linux') )
    self.assertEqual( [ '--foo', '--bar', '--macos' ],
                      psc.resolve_list(config, 'macos') )
    self.assertEqual( [ '--foo', '--bar', '--android' ],
                      psc.resolve_list(config, 'android') )
                        
  def test_resolve_dict(self):
    test_env = [
      'all: ALL=x',
      'android: A=1',
      'ios: I=2',
      'ios_sim: S=3',
      'linux: L=4',
      'macos: D=5',
    ]

    self.assertEqual( { 'ALL': 'x', 'A': '1' }, psc.resolve_key_values_to_dict(test_env, 'android') )
    self.assertEqual( { 'ALL': 'x', 'I': '2' }, psc.resolve_key_values_to_dict(test_env, System.IOS) )
    self.assertEqual( { 'ALL': 'x', 'S': '3' }, psc.resolve_key_values_to_dict(test_env, System.IOS_SIM) )
    self.assertEqual( { 'ALL': 'x', 'L': '4' }, psc.resolve_key_values_to_dict(test_env, 'linux') )
    self.assertEqual( { 'ALL': 'x', 'D': '5' }, psc.resolve_key_values_to_dict(test_env, 'macos') )

  def test_resolve_list(self):
    test_flags = [
      'all: -fall',
      'android: -f1',
      'ios: -f2',
      'linux: -f3',
      'macos: -f4',
      'android|macos: -f5',
    ]
    self.assertEqual( [ '-fall', '-f1', '-f5' ], psc.resolve_list(test_flags, 'android') )
    self.assertEqual( [ '-fall', '-f2' ], psc.resolve_list(test_flags, System.IOS) )
    self.assertEqual( [ '-fall', '-f3' ], psc.resolve_list(test_flags, 'linux') )
    self.assertEqual( [ '-fall', '-f4', '-f5' ], psc.resolve_list(test_flags, 'macos') )

  def test_resolve_list_string_mask(self):
    test_flags = [
      'ALL: -fall',
      'ANDROID: -f1',
      'IOS: -f2',
      'LINUX: -f3',
      'MACOS: -f4',
      'MACOS|ANDROID: -f5',
    ]
    self.assertEqual( [ '-fall', '-f1', '-f5' ], psc.resolve_list(test_flags, 'android') )
    self.assertEqual( [ '-fall', '-f2' ], psc.resolve_list(test_flags, System.IOS) )
    self.assertEqual( [ '-fall', '-f3' ], psc.resolve_list(test_flags, 'linux') )
    self.assertEqual( [ '-fall', '-f4', '-f5' ], psc.resolve_list(test_flags, 'macos') )

  def test_resolve_list_string_mask_lowercase(self):
    test_flags = [
      'all: -fall',
      'android: -f1',
      'ios: -f2',
      'linux: -f3',
      'macos: -f4',
      'macos|android: -f5',
    ]
    self.assertEqual( [ '-fall', '-f1', '-f5' ], psc.resolve_list(test_flags, 'android') )
    self.assertEqual( [ '-fall', '-f2' ], psc.resolve_list(test_flags, System.IOS) )
    self.assertEqual( [ '-fall', '-f3' ], psc.resolve_list(test_flags, 'linux') )
    self.assertEqual( [ '-fall', '-f4', '-f5' ], psc.resolve_list(test_flags, 'macos') )

  def test_parse_requirement(self):
    self.assertEqual( ( 'linux', [ ( 'foo', '>=', '1.2.3', 'linux' ) ] ),
                      psc.parse_requirement('linux: foo >= 1.2.3') )
    self.assertEqual( ( 'linux', [ ( 'foo', None, None, 'linux' ) ] ),
                      psc.parse_requirement('linux: foo') )
    self.assertEqual( ( 'linux', [ ( 'foo', '>=', '1.2.3', 'linux' ), ( 'bar', '>=', '6.6.6', 'linux' ) ] ),
                      psc.parse_requirement('linux: foo >= 1.2.3 bar >= 6.6.6') )
    self.assertEqual( ( 'linux', [ ( 'foo', '>=', '1.2.3', 'linux' ), ( 'bar', '>=', '6.6.6', 'linux' ) ] ),
                      psc.parse_requirement('linux: foo >= 1.2.3 bar(linux) >= 6.6.6') )
    self.assertEqual( ( 'linux', [ ( 'foo', '>=', '1.2.3', 'linux' ), ( 'bar', '>=', '6.6.6', 'linux|macos' ) ] ),
                      psc.parse_requirement('linux: foo >= 1.2.3 bar(linux|macos) >= 6.6.6') )
    self.assertEqual( ( 'linux', [ ( 'foo', '>=', '1.2.3', 'linux' ), ( 'bar', '>=', '6.6.6', 'macos' ) ] ),
                      psc.parse_requirement('linux: foo >= 1.2.3 bar(macos) >= 6.6.6') )

  def test_parse_requirement_with_system_aliases(self):
    self.assertEqual( ( 'all', [ ( 'foo', '>=', '1.2.3', 'all' ) ] ),
                      psc.parse_requirement('all: foo >= 1.2.3') )
    self.assertEqual( ( 'desktop', [ ( 'foo', '>=', '1.2.3', 'desktop' ) ] ),
                      psc.parse_requirement('desktop: foo >= 1.2.3') )

  def test_parse_requirement_with_system_override(self):
    self.assertEqual( ( 'all', [ ( 'foo', '>=', '1.2.3', 'linux' ) ] ),
                      psc.parse_requirement('all: foo(linux) >= 1.2.3') )

  def test_parse_requirement_empty_mask(self):
    self.assertEqual( ( None, [ ( 'foo', '>=', '1.2.3', None ) ] ),
                      psc.parse_requirement(': foo >= 1.2.3') )
#    self.assertEqual( ( None, [ ( 'foo', '>=', '1.2.3', None ), ( 'bar', '>=', '6.6.6', None ) ] ),
#                      psc.parse_requirement(': foo >= 1.2.3 bar >= 6.6.6') )

  def test_parse_requirement_per_req_system_mask(self):
    self.assertEqual( ( None, [ ( 'foo', '>=', '1.2.3', 'linux' ), ( 'bar', '>=', '6.6.6', 'macos' ) ] ),
                      psc.parse_requirement(': foo(linux) >= 1.2.3 bar(macos) >= 6.6.6') )

  def test_resolve_requirement(self):
    config = [
      'all: forall1 forall2',
      'linux: forlinux',
      'macos: formacos',
      'android: forandroid',
    ]
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'forlinux', None, None, None ) ],
                      psc.resolve_requirement(config, 'linux') )
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'formacos', None, None, None ) ],
                      psc.resolve_requirement(config, 'macos') )
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'forandroid', None, None, None ) ],
                      psc.resolve_requirement(config, 'android') )

  def test_resolve_requirement_empty_mask(self):
    config = [
      ': forall1 forall2',
    ]
    self.assertEqual( [], psc.resolve_requirement(config, 'linux') )
    self.assertEqual( [], psc.resolve_requirement(config, 'macos') )

  def test_resolve_requirement_empty_mask_per_req_system_mask(self):
    config = [
      ': forall1(all) forall2(all) forlinux(linux) formacos(macos)',
    ]
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'forlinux', None, None, None ) ],
                      psc.resolve_requirement(config, 'linux') )

    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'formacos', None, None, None ) ],
                      psc.resolve_requirement(config, 'macos') )

  def test_resolve_requirement_global_mask_and_per_req_system_masks(self):
    config = [
      'all: forall1 forall2 forlinux(linux) formacos(macos)',
    ]
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'forlinux', None, None, None ) ],
                      psc.resolve_requirement(config, 'linux') )
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'formacos', None, None, None ) ],
                      psc.resolve_requirement(config, 'macos') )
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ) ],
                      psc.resolve_requirement(config, 'android') )


  def test_resolve_requirement_global_mask_and_per_req_system_masks(self):
    config = [
      'all: forall1 forall2 forlinux(linux) formacos(macos)',
    ]
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'forlinux', None, None, None ) ],
                      psc.resolve_requirement(config, 'linux') )
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'formacos', None, None, None ) ],
                      psc.resolve_requirement(config, 'macos') )
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ) ],
                      psc.resolve_requirement(config, 'android') )

  def test_resolve_list_with_colons(self):
    config = [
      'all: orange:foo apple:bar',
      'linux: pear:baz',
      'macos: kiwi:hhh',
    ]
    self.assertEqual( [ 'orange:foo', 'apple:bar', 'pear:baz' ],
                      psc.resolve_list(config, 'linux') )
    self.assertEqual( [ 'orange:foo', 'apple:bar', 'kiwi:hhh' ],
                      psc.resolve_list(config, 'macos') )
    self.assertEqual( [ 'orange:foo', 'apple:bar' ],
                      psc.resolve_list(config, 'android') )

if __name__ == "__main__":
  unit_test.main()

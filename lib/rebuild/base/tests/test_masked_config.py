#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from bes.key_value import key_value
from rebuild.base import masked_config as MC
from rebuild.base import build_system

class test_masked_config(unit_test):

  def test_simple(self):
    self.assertEqual( ( 'linux', 'foo bar baz' ), MC.parse('linux: foo bar baz') )

  def test_simple_var(self):
    self.assertEqual( ( 'linux', '${foo} ${bar} ${baz}' ), MC.parse('linux: ${foo} ${bar} ${baz}') )
    
  def test_simple_white_space(self):
    self.assertEqual( ( 'linux', 'foo bar baz' ), MC.parse('linux:      foo bar baz     ') )

  def test_key_values(self):
    self.assertEqual( ( 'linux', [ ( 'foo', '5' ), ( 'bar', 'hi' ) ] ), MC.parse_key_values('linux: foo=5 bar=hi') )

  def test_key_values_with_spaces(self):
    self.assertEqual( ( 'linux', [ ( 'foo', '"1 2 3"' ), ( 'bar', "'a b c'" ) ] ), MC.parse_key_values('linux: foo="1 2 3" bar=\'a b c\'') )
    self.assertEqual( ( 'linux', [ ( 'foo', '"1 2 3"' ), ( 'bar', None ) ] ), MC.parse_key_values('linux: foo="1 2 3" bar=') )

  def test_parse_list(self):
    self.assertEqual( ( 'linux', [ '--foo', '--bar', 'BAZ="a b c"' ] ), MC.parse_list('linux: --foo --bar BAZ=\"a b c\"') )
    self.assertEqual( ( 'linux', [ 'foo="a b c"' ] ), MC.parse_list('linux: foo="a b c"') )
    self.assertEqual( ( 'linux', [ 'CFLAGS="-f foo -g bar"' ] ), MC.parse_list(r'linux: CFLAGS="-f foo -g bar"') )

  def test_key_values_with_vars(self):
    self.assertEqual( ( 'linux', [ ( 'foo', '${a}' ) ] ), MC.parse_key_values('linux: foo=${a}') )
    
  def test_resolve_key_values(self):
    config = [
      'all: foo=666 bar=hi',
      'linux: creator=linus',
      'macos: creator=steve',
      'android: creator=andy',
    ]
    self.assertEqual( [ key_value('foo', '666'), key_value('bar', 'hi'), key_value('creator', 'linus') ],
                      MC.resolve_key_values(config, 'linux') )
    self.assertEqual( [ key_value('foo', '666'), key_value('bar', 'hi'), key_value('creator', 'steve') ],
                      MC.resolve_key_values(config, 'macos') )
    self.assertEqual( [ key_value('foo', '666'), key_value('bar', 'hi'), key_value('creator', 'andy') ],
                      MC.resolve_key_values(config, 'android') )
                        
  def test_resolve_key_values_duplicate_keys(self):
    config = [
      'all: foo=666',
      'linux: creator=linus',
      'macos: creator=steve',
      'android: creator=andy',
      'linux|macos: creator=engineers',
    ]
    self.assertEqual( [ key_value('foo', '666'), key_value('creator', 'linus'), key_value('creator', 'engineers') ],
                      MC.resolve_key_values(config, 'linux') )
    self.assertEqual( [ key_value('foo', '666'), key_value('creator', 'steve'), key_value('creator', 'engineers') ],
                      MC.resolve_key_values(config, 'macos') )
    self.assertEqual( [ key_value('foo', '666'), key_value('creator', 'andy') ],
                      MC.resolve_key_values(config, 'android') )

  def test_resolve_key_values_to_dict(self):
    config = [
      'all: foo=666 bar=hi',
      'linux: creator=linus',
      'macos: creator=steve',
      'android: creator=andy',
    ]
    self.assertEqual( { 'foo': '666', 'bar': 'hi', 'creator': 'linus' },
                      MC.resolve_key_values_to_dict(config, 'linux') )
    self.assertEqual( { 'foo': '666', 'bar': 'hi', 'creator': 'steve' },
                      MC.resolve_key_values_to_dict(config, 'macos') )
    self.assertEqual( { 'foo': '666', 'bar': 'hi', 'creator': 'andy' },
                      MC.resolve_key_values_to_dict(config, 'android') )
                        
  def test_resolve_key_values_to_dict_duplicate_keys(self):
    config = [
      'all: foo=666',
      'linux: creator=linus',
      'macos: creator=steve',
      'android: creator=andy',
      'linux|macos: creator=engineers',
    ]
    self.assertEqual( { 'foo': '666', 'creator': 'engineers' },
                      MC.resolve_key_values_to_dict(config, 'linux') )
    self.assertEqual( { 'foo': '666', 'creator': 'engineers' },
                      MC.resolve_key_values_to_dict(config, 'macos') )
    self.assertEqual( { 'foo': '666', 'creator': 'andy' },
                      MC.resolve_key_values_to_dict(config, 'android') )
                        
  def test_resolve_list(self):
    config = [
      'all: --foo --bar',
      'linux: --linux',
      'macos: --macos',
      'android: --android',
    ]
    self.assertEqual( [ '--foo', '--bar', '--linux' ],
                      MC.resolve_list(config, 'linux') )
    self.assertEqual( [ '--foo', '--bar', '--macos' ],
                      MC.resolve_list(config, 'macos') )
    self.assertEqual( [ '--foo', '--bar', '--android' ],
                      MC.resolve_list(config, 'android') )
                        
  def test_resolve_dict(self):
    test_env = [
      'all: ALL=x',
      'android: A=1',
      'ios: I=2',
      'ios_sim: S=3',
      'linux: L=4',
      'macos: D=5',
    ]

    self.assertEqual( { 'ALL': 'x', 'A': '1' }, MC.resolve_key_values_to_dict(test_env, 'android') )
    self.assertEqual( { 'ALL': 'x', 'I': '2' }, MC.resolve_key_values_to_dict(test_env, build_system.IOS) )
    self.assertEqual( { 'ALL': 'x', 'S': '3' }, MC.resolve_key_values_to_dict(test_env, build_system.IOS_SIM) )
    self.assertEqual( { 'ALL': 'x', 'L': '4' }, MC.resolve_key_values_to_dict(test_env, 'linux') )
    self.assertEqual( { 'ALL': 'x', 'D': '5' }, MC.resolve_key_values_to_dict(test_env, 'macos') )

  def test_resolve_list(self):
    test_flags = [
      'all: -fall',
      'android: -f1',
      'ios: -f2',
      'linux: -f3',
      'macos: -f4',
      'android|macos: -f5',
    ]
    self.assertEqual( [ '-fall', '-f1', '-f5' ], MC.resolve_list(test_flags, 'android') )
    self.assertEqual( [ '-fall', '-f2' ], MC.resolve_list(test_flags, build_system.IOS) )
    self.assertEqual( [ '-fall', '-f3' ], MC.resolve_list(test_flags, 'linux') )
    self.assertEqual( [ '-fall', '-f4', '-f5' ], MC.resolve_list(test_flags, 'macos') )

  def test_resolve_list_string_mask(self):
    test_flags = [
      'ALL: -fall',
      'ANDROID: -f1',
      'IOS: -f2',
      'LINUX: -f3',
      'MACOS: -f4',
      'MACOS|ANDROID: -f5',
    ]
    self.assertEqual( [ '-fall', '-f1', '-f5' ], MC.resolve_list(test_flags, 'android') )
    self.assertEqual( [ '-fall', '-f2' ], MC.resolve_list(test_flags, build_system.IOS) )
    self.assertEqual( [ '-fall', '-f3' ], MC.resolve_list(test_flags, 'linux') )
    self.assertEqual( [ '-fall', '-f4', '-f5' ], MC.resolve_list(test_flags, 'macos') )

  def test_resolve_list_string_mask_lowercase(self):
    test_flags = [
      'all: -fall',
      'android: -f1',
      'ios: -f2',
      'linux: -f3',
      'macos: -f4',
      'macos|android: -f5',
    ]
    self.assertEqual( [ '-fall', '-f1', '-f5' ], MC.resolve_list(test_flags, 'android') )
    self.assertEqual( [ '-fall', '-f2' ], MC.resolve_list(test_flags, build_system.IOS) )
    self.assertEqual( [ '-fall', '-f3' ], MC.resolve_list(test_flags, 'linux') )
    self.assertEqual( [ '-fall', '-f4', '-f5' ], MC.resolve_list(test_flags, 'macos') )

  def test_parse_requirement(self):
    self.assertEqual( ( 'linux', [ ( 'foo', '>=', '1.2.3', 'linux' ) ] ),
                      MC.parse_requirement('linux: foo >= 1.2.3') )
    self.assertEqual( ( 'linux', [ ( 'foo', None, None, 'linux' ) ] ),
                      MC.parse_requirement('linux: foo') )
    self.assertEqual( ( 'linux', [ ( 'foo', '>=', '1.2.3', 'linux' ), ( 'bar', '>=', '6.6.6', 'linux' ) ] ),
                      MC.parse_requirement('linux: foo >= 1.2.3 bar >= 6.6.6') )
    self.assertEqual( ( 'linux', [ ( 'foo', '>=', '1.2.3', 'linux' ), ( 'bar', '>=', '6.6.6', 'linux' ) ] ),
                      MC.parse_requirement('linux: foo >= 1.2.3 bar(linux) >= 6.6.6') )
    self.assertEqual( ( 'linux', [ ( 'foo', '>=', '1.2.3', 'linux' ), ( 'bar', '>=', '6.6.6', 'linux|macos' ) ] ),
                      MC.parse_requirement('linux: foo >= 1.2.3 bar(linux|macos) >= 6.6.6') )
    self.assertEqual( ( 'linux', [ ( 'foo', '>=', '1.2.3', 'linux' ), ( 'bar', '>=', '6.6.6', 'macos' ) ] ),
                      MC.parse_requirement('linux: foo >= 1.2.3 bar(macos) >= 6.6.6') )

  def test_parse_requirement_with_system_aliases(self):
    self.assertEqual( ( 'all', [ ( 'foo', '>=', '1.2.3', 'all' ) ] ),
                      MC.parse_requirement('all: foo >= 1.2.3') )
    self.assertEqual( ( 'desktop', [ ( 'foo', '>=', '1.2.3', 'desktop' ) ] ),
                      MC.parse_requirement('desktop: foo >= 1.2.3') )

  def test_parse_requirement_with_system_override(self):
    self.assertEqual( ( 'all', [ ( 'foo', '>=', '1.2.3', 'linux' ) ] ),
                      MC.parse_requirement('all: foo(linux) >= 1.2.3') )

  def test_parse_requirement_empty_mask(self):
    self.assertEqual( ( None, [ ( 'foo', '>=', '1.2.3', None ) ] ),
                      MC.parse_requirement(': foo >= 1.2.3') )
#    self.assertEqual( ( None, [ ( 'foo', '>=', '1.2.3', None ), ( 'bar', '>=', '6.6.6', None ) ] ),
#                      MC.parse_requirement(': foo >= 1.2.3 bar >= 6.6.6') )

  def test_parse_requirement_per_req_system_mask(self):
    self.assertEqual( ( None, [ ( 'foo', '>=', '1.2.3', 'linux' ), ( 'bar', '>=', '6.6.6', 'macos' ) ] ),
                      MC.parse_requirement(': foo(linux) >= 1.2.3 bar(macos) >= 6.6.6') )

  def test_resolve_requirement(self):
    config = [
      'all: forall1 forall2',
      'linux: forlinux',
      'macos: formacos',
      'android: forandroid',
    ]
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'forlinux', None, None, None ) ],
                      MC.resolve_requirement(config, 'linux') )
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'formacos', None, None, None ) ],
                      MC.resolve_requirement(config, 'macos') )
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'forandroid', None, None, None ) ],
                      MC.resolve_requirement(config, 'android') )

  def test_resolve_requirement_empty_mask(self):
    config = [
      ': forall1 forall2',
    ]
    self.assertEqual( [], MC.resolve_requirement(config, 'linux') )
    self.assertEqual( [], MC.resolve_requirement(config, 'macos') )

  def test_resolve_requirement_empty_mask_per_req_system_mask(self):
    config = [
      ': forall1(all) forall2(all) forlinux(linux) formacos(macos)',
    ]
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'forlinux', None, None, None ) ],
                      MC.resolve_requirement(config, 'linux') )

    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'formacos', None, None, None ) ],
                      MC.resolve_requirement(config, 'macos') )

  def test_resolve_requirement_global_mask_and_per_req_system_masks(self):
    config = [
      'all: forall1 forall2 forlinux(linux) formacos(macos)',
    ]
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'forlinux', None, None, None ) ],
                      MC.resolve_requirement(config, 'linux') )
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'formacos', None, None, None ) ],
                      MC.resolve_requirement(config, 'macos') )
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ) ],
                      MC.resolve_requirement(config, 'android') )


  def test_resolve_requirement_global_mask_and_per_req_system_masks(self):
    config = [
      'all: forall1 forall2 forlinux(linux) formacos(macos)',
    ]
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'forlinux', None, None, None ) ],
                      MC.resolve_requirement(config, 'linux') )
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ), ( 'formacos', None, None, None ) ],
                      MC.resolve_requirement(config, 'macos') )
    self.assertEqual( [ ( 'forall1', None, None, None ), ( 'forall2', None, None, None ) ],
                      MC.resolve_requirement(config, 'android') )

  def test_resolve_requirement_global_mask(self):
    config = [
      'macos: foo >= 1.0 bar >= 2.0 baz >= 3.0 kiwi >= 4.0',
    ]
    self.assertEqual( [
      ( 'foo', '>=', '1.0', None ),
      ( 'bar', '>=', '2.0', None ),
      ( 'baz', '>=', '3.0', None ),
      ( 'kiwi', '>=', '4.0', None ),
    ], MC.resolve_requirement(config, 'macos') )
    
    self.assertEqual( [], MC.resolve_requirement(config, 'linux') )
    
  def test_resolve_list_with_colons(self):
    config = [
      'all: orange:foo apple:bar',
      'linux: pear:baz',
      'macos: kiwi:hhh',
    ]
    self.assertEqual( [ 'orange:foo', 'apple:bar', 'pear:baz' ],
                      MC.resolve_list(config, 'linux') )
    self.assertEqual( [ 'orange:foo', 'apple:bar', 'kiwi:hhh' ],
                      MC.resolve_list(config, 'macos') )
    self.assertEqual( [ 'orange:foo', 'apple:bar' ],
                      MC.resolve_list(config, 'android') )

if __name__ == "__main__":
  unit_test.main()

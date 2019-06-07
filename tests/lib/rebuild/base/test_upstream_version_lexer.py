#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text.lexer_token import lexer_token
from bes.common.point import point

from rebuild.base.upstream_version_lexer import upstream_version_lexer

def TDONE(x = 1, y = 1): return lexer_token(upstream_version_lexer.TOKEN_DONE, None, point(x, y))
def TTEXT(s, x = 1, y = 1): return lexer_token(upstream_version_lexer.TOKEN_TEXT, s, point(x, y))
def TPUNCT(s, x = 1, y = 1): return lexer_token(upstream_version_lexer.TOKEN_PUNCTUATION, s, point(x, y))
def TNUM(s, x = 1, y = 1): return lexer_token(upstream_version_lexer.TOKEN_NUMBER, s, point(x, y))

class test_upstream_version_lexer(unit_test):

  def test_empty_string(self):
    self.assertEqual( [ TDONE() ],
                      self._tokenize(r'') )

  def test_single_char(self):
    self.assertEqual( [ TTEXT('a'), TDONE() ],
                      self._tokenize(r'a') )

  def test_dual_char(self):
    self.assertEqual( [ TTEXT('ab'), TDONE() ],
                      self._tokenize(r'ab') )

  def test_single_number(self):
    self.assertEqual( [ TNUM(1), TDONE() ],
                      self._tokenize(r'1') )

  def test_dual_number(self):
    self.assertEqual( [ TNUM(12), TDONE() ],
                      self._tokenize(r'12') )
    
  def test_single_punct(self):
    self.assertEqual( [ TPUNCT('-'), TDONE() ],
                      self._tokenize(r'-') )

  def test_dual_punct(self):
    self.assertEqual( [ TPUNCT('--'), TDONE() ],
                      self._tokenize(r'--') )
    
  def test_number_and_text(self):
    self.assertEqual( [ TNUM(1), TTEXT('a'), TDONE() ],
                      self._tokenize(r'1a') )
    
  def test_text_and_number(self):
    self.assertEqual( [ TTEXT('a'), TNUM(1), TDONE() ],
                      self._tokenize(r'a1') )
    
  def test_text_punct_and_number(self):
    self.assertEqual( [ TNUM(1), TPUNCT('.'), TTEXT('a'), TDONE() ],
                      self._tokenize(r'1.a') )
    
  def test_build_version(self):
    self.assertEqual( [ TNUM(1), TPUNCT('.'), TNUM(2), TPUNCT('.'), TNUM(3), TDONE() ],
                      self._tokenize(r'1.2.3') )

  def test_build_version_with_alpha(self):
    self.assertEqual( [ TNUM(1), TPUNCT('.'), TNUM(2), TPUNCT('.'), TNUM(3), TTEXT('a'), TDONE() ],
                      self._tokenize(r'1.2.3a') )
    
  @classmethod
  def _tokenize(self, text):
    return [ token for token in upstream_version_lexer.tokenize(text, 'unit_test') ]

  def assertEqual(self, expected, actual):
    assert isinstance(expected, list)
    expected = [ lexer_token(*t) for t in expected ]
    super(test_upstream_version_lexer, self).assertEqual(expected, actual)

if __name__ == '__main__':
  unit_test.main()

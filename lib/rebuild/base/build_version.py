#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.common.number_util import number_util
from bes.common.tuple_util import tuple_util
from collections import namedtuple
from bes.compat.StringIO import StringIO
from bes.compat.cmp import cmp
from .upstream_version_lexer import upstream_version_lexer

class build_version(namedtuple('build_version', 'upstream_version, revision, epoch')):
  '''
  Manage package versions.  Inspired by the debian version format described here:

    https://www.debian.org/doc/debian-policy/ch-controlfields.html

  Notable deviations from the debian format:
    o Hyphens are never allowed in "upstream_version" regardless of the presence of "revision"
    o Colons are never allowed in either "upstream_version" or "revision" regardless of the presence of "epoch"
  '''

  def __new__(clazz, upstream_version, revision, epoch):
    upstream_version = clazz.validate_upstream_version(upstream_version)
    revision = clazz.validate_revision(revision)
    epoch = clazz.validate_epoch(epoch)
    return clazz.__bases__[0].__new__(clazz, upstream_version, revision, epoch)

  _validation = namedtuple('_validation', 'valid,error')
  
  @classmethod
  def upstream_version_is_valid(clazz, upstream_version):
    return clazz._upstream_version_is_valid(upstream_version).valid

  @classmethod
  def validate_upstream_version(clazz, upstream_version):
    validation = clazz._upstream_version_is_valid(upstream_version)
    if not validation.valid:
      raise RuntimeError(validation.error)
    return upstream_version

  @classmethod
  def _upstream_version_is_valid(clazz, upstream_version):
    if not string_util.is_string(upstream_version):
      return clazz._validation(False, 'invalid upstream_version of type %s - should be string: \"%s\"' % (type(upstream_version), str(upstream_version)))
    if upstream_version == None:
      return clazz._validation(False, 'upstream_version is None')
    if upstream_version == '':
      return clazz._validation(False, 'upstream_version is empty')
    for c in upstream_version:
      if not clazz._upstream_char_is_valid(c):
        return clazz._validation(False, 'invalid character \"%s\" in upstream_version \"%s\"' % (c, upstream_version))
    if not upstream_version[0].isalnum():
      return clazz._validation(False, 'upstream_version should start with a alphanumeric: \"%s\"' % (upstream_version))
    return clazz._validation(True, None)
  
  @classmethod
  def _upstream_char_is_valid(clazz, c):
    return c.isalnum() or c in [ '.', '+', '~', '_' ]
    
  @classmethod
  def epoch_is_valid(clazz, epoch):
    return number_util.string_is_int(epoch)
  
  @classmethod
  def validate_epoch(clazz, epoch):
    return clazz._validate_epoch_revision(epoch, 'epoch')
  
  @classmethod
  def revision_is_valid(clazz, revision):
    return number_util.string_is_int(revision)
  
  @classmethod
  def validate_revision(clazz, revision):
    return clazz._validate_epoch_revision(revision, 'revision')

  @classmethod
  def _validate_epoch_revision(clazz, n, label):
    if not number_util.string_is_int(n):
      raise RuntimeError('invalid %s of type %s - should be int: \"%s\"' % (label, type(n), str(n)))
    return int(n)
  
  def __str__(self):
    buf = StringIO()
    if self.epoch != 0:
      buf.write(str(self.epoch))
      buf.write(':')
    buf.write(str(self.upstream_version))
    if self.revision != 0:
      buf.write('-')
      buf.write(str(self.revision))
    return buf.getvalue()

  @classmethod
  def parse(clazz, text):
    v = text.partition(':')
    if v[1] == ':':
      epoch = v[0]
      right = v[2]
    else:
      epoch = 0
      right = v[0]
    v = right.partition('-')
    if v[1] == '-':
      revision = v[2]
      upstream_version = v[0]
    else:
      revision = 0
      upstream_version = v[0]
    return clazz(upstream_version, revision, epoch)

  @classmethod
  def validate_version(clazz, v):
    if isinstance(v, build_version):
      return v
    return build_version.parse(v)

  @classmethod
  def compare(clazz, v1, v2):
    epoch_cmp = cmp(v1.epoch, v2.epoch)
    if epoch_cmp != 0:
      return epoch_cmp
    upstream_version_cmp = clazz.compare_upstream_version(v1.upstream_version, v2.upstream_version)
    if upstream_version_cmp != 0:
      return upstream_version_cmp
    return cmp(v1.revision, v2.revision)

  @classmethod
  def _cast_build_version(clazz, v):
    if check.is_tuple(v):
      return build_version(*v)
    return v
  
  def __eq__(self, other):
    other = self._cast_build_version(other)
    check.check_build_version(other)
    return self.compare(self, other) == 0
    
  def __lt__(self, other):
    other = self._cast_build_version(other)
    check.check_build_version(other)
    return self.compare(self, other) < 0
    
  def __le__(self, other):
    other = self._cast_build_version(other)
    check.check_build_version(other)
    return self.compare(self, other) <= 0
    
  def __gt__(self, other):
    other = self._cast_build_version(other)
    check.check_build_version(other)
    return self.compare(self, other) > 0
    
  def __ge__(self, other):
    other = self._cast_build_version(other)
    check.check_build_version(other)
    return self.compare(self, other) >= 0
    
  # This function should implement exactly the algorithm described here (its close):
  # https://manpages.debian.org/wheezy/dpkg-dev/deb-version.5.en.html#Sorting_Algorithm
  @classmethod
  def compare_upstream_version(clazz, v1, v2):
    check.check_string(v1)
    check.check_string(v2)
    tokens1 = [ token for token in upstream_version_lexer.tokenize(v1, 'build_version') ]
    tokens2 = [ token for token in upstream_version_lexer.tokenize(v2, 'build_version') ]
    return cmp(tokens1, tokens2)

  @classmethod
  def compare_version_and_revision(clazz, v1, r1, v2, r2):
    check.check_string(v1)
    check.check_int(r1)
    check.check_string(v2)
    check.check_int(r2)
    assert '-' not in v1
    assert '-' not in v2
    s1 = '%s-%d' % (v1, r1)
    s2 = '%s-%d' % (v2, r2)
    return clazz.compare_upstream_version(s1, s2)
  
  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
check.register_class(build_version)

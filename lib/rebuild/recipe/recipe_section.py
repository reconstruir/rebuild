#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import algorithm, dict_util
from bes.common.check_type import check_type
from bes.key_value import key_value, key_value_list
from StringIO import StringIO

class recipe_section(object):

  def __init__(self, header, values):
    check_type(header, key_value, 'header')
    if not header.key:
      raise TypeError('header key should not be empty: %s' % (header.key))
    if not header.value:
      raise TypeError('header value should not be empty: %s' % (header.value))
    if not header.is_homogeneous(basestring, basestring):
      raise TypeError('invalid header.  key and value should be strings: %s' % (header))
    self.header = header
    values = key_value_list.verify_key_value_list(values or [])
    if values is None:
      raise TypeError('values should be a key_value_list or iterable of key_values: %s' % (values))
    if not values.is_homogeneous(basestring, basestring):
      raise TypeError('invalid values.  all keys and values should be strings: %s' % (values))
    self.values = values
    assert isinstance(self.values, key_value_list)

  def __str__(self):
    buf = StringIO()
    delimiter = ': '
    value_delimiter = '\n'
    buf.write(self.header.to_string(delimiter = delimiter))
    buf.write(value_delimiter)
    buf.write(self.values.to_string(delimiter = delimiter, value_delimiter = value_delimiter))
    return buf.getvalue()

#  def __repr__(self):
#    return str(self)

  def __eq__(self, other):
    print "HERE:   self: %s - %s" % (self.header, self.values)
    print "HERE:  other: %s - %s" % (other.header, other.values)
    return self.__dict__ == other.__dict__

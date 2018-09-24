#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from collections import namedtuple
from bes.common import check

class pcloud_credentials(namedtuple('pcloud_credentials', 'email, password')):
  
  def __new__(clazz, email, password):
    return clazz.__bases__[0].__new__(clazz, email, password)

  def is_valid(self):
    return self.email and self.password

  @classmethod
  def from_file(clazz, filename):
    content = file_util.read(filename)
    d = json.loads(content)
    return clazz.parse_dict(d)
  
  @classmethod
  def from_file(clazz, filename):
    content = file_util.read(filename)
    d = json.loads(content)
    return clazz.parse_dict(d)

  @classmethod
  def from_environment(clazz):
    email = os.environ.get('PCLOUD_EMAIL', None)
    password = os.environ.get('PCLOUD_PASSWORD', None)
    return clazz(email, password)

  @classmethod
  def from_command_line_args(clazz, email, password):
    if email and not password:
      raise RuntimeError('email given but no password')
    if password and not email:
      raise RuntimeError('password given but no email')
    return clazz(email, password)

  @classmethod
  def parse_dict(clazz, d):
    check.check_dict(d)
    assert 'email' in d
    assert 'password' in d
    return clazz(d['email'], d['password'])
  
check.register_class(pcloud_credentials)

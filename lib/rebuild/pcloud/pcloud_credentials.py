#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os
from collections import namedtuple
from bes.common import check
from bes.fs import file_util

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
  
  @classmethod
  def add_command_line_args(clazz, parser):
    parser.add_argument('-E', '--email',
                        action = 'store',
                        default = None,
                        type = str,
                        help = 'The pcloud account password. [ None ]')
    parser.add_argument('-P', '--password',
                        action = 'store',
                        default = None,
                        type = str,
                        help = 'The pcloud account password. [ None ]')
    parser.add_argument('--credentials',
                        action = 'store',
                        default = None,
                        type = str,
                        help = 'A pcloud credentials file. [ None ]')

  @classmethod
  def resolve_command_line(clazz, args):
    if args.credentials:
      credentials = pcloud_credentials.from_file(args.credentials)
    elif args.email or args.password:
      credentials = pcloud_credentials.from_command_line_args(args.email, args.password)
      del args.email
      del args.password
    else:
      credentials = pcloud_credentials.from_environment()
    return credentials
    
check.register_class(pcloud_credentials)

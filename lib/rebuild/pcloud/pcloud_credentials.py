#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os
from collections import namedtuple
from bes.common import check
from bes.fs import file_util

class pcloud_credentials(namedtuple('pcloud_credentials', 'email, password, root_dir')):
  
  def __new__(clazz, email, password, root_dir):
    return clazz.__bases__[0].__new__(clazz, email, password, root_dir)

  def is_valid(self):
    return self.email and self.password and self.root_dir

  def validate_or_bail(self):
    if self.is_valid():
      return
    if not self.email:
      print('No pcloud email given.  Set PCLOUD_EMAIL or use the --pcloud-email flag')
    if not self.password:
      print('No pcloud password given.  Set PCLOUD_PASSWORD or use the --pcloud-password flag')
    if not self.root_dir:
      print('No pcloud root_dir given.  Set PCLOUD_ROOT_DIR or use the --pcloud-root-dir flag')
    raise SystemExit(1)
  
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
    credentials = os.environ.get('PCLOUD_CREDENTIALS', None)
    if credentials:
      return pcloud_credentials.from_file(credentials)
    email = os.environ.get('PCLOUD_EMAIL', None)
    password = os.environ.get('PCLOUD_PASSWORD', None)
    root_dir = os.environ.get('PCLOUD_ROOT_DIR', None)
    return clazz(email, password, root_dir)

  @classmethod
  def from_command_line_args(clazz, email, password, root_dir):
    if not email:
      raise RuntimeError('email not given')
    if not password:
      raise RuntimeError('password not given')
    if not root_dir:
      raise RuntimeError('root_dir not given')
    return clazz(email, password, root_dir)

  @classmethod
  def parse_dict(clazz, d):
    check.check_dict(d)
    assert 'email' in d
    assert 'password' in d
    assert 'root_dir' in d
    return clazz(d['email'], d['password'], d['root_dir'])
  
  @classmethod
  def add_command_line_args(clazz, parser):
    parser.add_argument('--pcloud-email',
                        action = 'store',
                        default = None,
                        type = str,
                        help = 'The pcloud account password. [ None ]')
    parser.add_argument('--pcloud-password',
                        action = 'store',
                        default = None,
                        type = str,
                        help = 'The pcloud account password. [ None ]')
    parser.add_argument('--pcloud-root-dir',
                        action = 'store',
                        default = None,
                        type = str,
                        help = 'The pcloud account root dir. [ None ]')
    parser.add_argument('--pcloud-credentials',
                        action = 'store',
                        default = None,
                        type = str,
                        help = 'A pcloud credentials file. [ None ]')

  @classmethod
  def resolve_command_line(clazz, args):
    if args.pcloud_credentials:
      credentials = pcloud_credentials.from_file(args.pcloud_credentials)
    elif args.pcloud_email or args.pcloud_password or args.pcloud_root_dir:
      credentials = pcloud_credentials.from_command_line_args(args.pcloud_email, args.pcloud_password, args.pcloud_root_dir)
    else:
      credentials = pcloud_credentials.from_environment()
    del args.pcloud_email
    del args.pcloud_password
    del args.pcloud_root_dir
    del args.pcloud_credentials
    return credentials
    
check.register_class(pcloud_credentials)

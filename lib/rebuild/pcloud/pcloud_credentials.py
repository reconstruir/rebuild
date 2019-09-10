#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os
from collections import namedtuple
from bes.common.check import check
from bes.fs.file_util import file_util

from rebuild.credentials.credentials import credentials

class pcloud_credentials(object):
  
  @classmethod
  def from_environment(clazz):
    return credentials('<env>', email = '${PCLOUD_EMAIL}', password = '${PCLOUD_PASSWORD}')

  @classmethod
  def from_command_line_args(clazz, email, password):
    if not email:
      raise RuntimeError('email not given')
    if not password:
      raise RuntimeError('password not given')
    return credentials('<cli>', email = email, password = password)

  @classmethod
  def parse_dict(clazz, d):
    check.check_dict(d)
    assert 'email' in d
    assert 'password' in d
    return credentials('<dict>', email = d['email'], password = d['password'])
  
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
    parser.add_argument('--pcloud-credentials',
                        action = 'store',
                        default = None,
                        type = str,
                        help = 'A pcloud credentials file. [ None ]')

  @classmethod
  def resolve_command_line(clazz, args):
    if args.pcloud_credentials:
      credentials = pcloud_credentials.from_file(args.pcloud_credentials)
    elif args.pcloud_email or args.pcloud_password:
      credentials = pcloud_credentials.from_command_line_args(args.pcloud_email, args.pcloud_password)
    else:
      credentials = pcloud_credentials.from_environment()
    del args.pcloud_email
    del args.pcloud_password
    del args.pcloud_credentials
    return credentials
    
check.register_class(pcloud_credentials)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

import requests

from bes.common.check import check
from bes.common.node import node
from bes.fs.file_attributes import file_attributes
from bes.fs.file_checksum import file_checksum
from bes.fs.file_checksum_db import file_checksum_db
from bes.fs.file_find import file_find
from bes.fs.file_metadata import file_metadata
from bes.fs.file_util import file_util
from bes.system.log import logger
from bes.factory.factory_field import factory_field

from bes.fs.fs.fs_base import fs_base
from bes.fs.fs.fs_file_info import fs_file_info
from bes.fs.fs.fs_file_info_list import fs_file_info_list
from bes.fs.fs.fs_error import fs_error

from rebuild.credentials.credentials import credentials

#from .artifactory import artifactory

class fs_artifactory(fs_base):
  'artifactory filesystem'

  log = logger('fs')
  
  def __init__(self, address, credentials, cache_dir = None):
    check.check_string(address)
    check.check_credentials(credentials)
    check.check_string(cache_dir, allow_none = True)
    self._address = address
    self._credentials = credentials
    self._cache_dir = cache_dir or path.expanduser('~/.besfs/fs_artifactory/cache')
    #self._artifactory = artifactory(credentials, root_dir or '/')

  def __str__(self):
    return 'fs_artifactory({}@{})'.format(self._credentials.username, self._address)

  @classmethod
  #@abstractmethod
  def creation_fields(clazz):
    'Return a list of fields needed for create()'
    return [
      factory_field('artifactory_username', False, check.is_string),
      factory_field('artifactory_password', False, check.is_string),
      factory_field('artifactory_address', False, check.is_string),
      factory_field('artifactory_cache_dir', True, check.is_string),
    ]
  
  @classmethod
  #@abstractmethod
  def create(clazz, **values):
    'Create an fs_artifactory instance.'
    cred = credentials.make_credentials(username = values['artifactory_username'],
                                        password = values['artifactory_password'])
    return fs_artifactory(values['artifactory_address'],
                          cred,
                          cache_dir = values['artifactory_cache_dir'])
    
  @classmethod
  #@abstractmethod
  def name(clazz):
    'The name if this fs.'
    return 'fs_artifactory'

  #@abstractmethod
  def list_dir(self, remote_dir, recursive):
    'List entries in a directory.'
    remote_dir = file_util.ensure_lsep(remote_dir)

    url = '{}/api/storage{}?list&deep=100&depth=1&listFolders=1'.format(self._address, remote_dir)

    print('url: {}'.format(url))
    
    auth = ( self._credentials.username, self._credentials.password )
    response = requests.get(url, auth = auth)
    response_data = response.json()
    entries = response_data['files']
    children = fs_file_info_list([ self._convert_artifactory_entry_to_fs_tree(entry, depth = 0) for entry in entries ])
    return fs_file_info(remote_dir, fs_file_info.DIR, None, None, None, children)

  def _convert_artifactory_entry_to_fs_tree(self, entry, depth = 0):
    print('CONVERTING: {}'.format(entry))
    indent = ' ' * depth
    is_file = not entry['folder']
    remote_filename = entry['uri']
    if is_file:
      children = fs_file_info_list()
    else:
      children = fs_file_info_list([ self._convert_artifactory_entry_to_fs_tree(n, depth + 2) for n in entry.children or [] ])
    return self._make_entry(remote_filename, entry, children)
    
  #@abstractmethod
  def has_file(self, remote_filename):
    'Return True if filename exists in the filesystem and is a FILE.'
    try:
      self.file_info(remote_filename)
      return True
    except fs_error as ex:
      return False
  
  #@abstractmethod
  def file_info(self, remote_filename):
    'Get info for a single file.'

    remote_filename = file_util.ensure_lsep(remote_filename)
    if remote_filename == '/':
      return fs_file_info(remote_filename, fs_file_info.DIR, None, None, None, fs_file_info_list())
    
    url = '{}/api/storage{}'.format(self._address, remote_filename)
    print('url: {}'.format(url))
    auth = ( self._credentials.username, self._credentials.password )
    response = requests.get(url, auth = auth)
    print('response: {}'.format(response))
    if response.status_code != 200:
      raise fs_error('file not found: {}'.format(remote_filename))
      
    data = response.json()
    if 'children' in data:
      ftype = fs_file_info.DIR
    else:
      ftype = fs_file_info.FILE

    if ftype == fs_file_info.FILE:
      checksum = data['checksums']['sha256']
      attributes = {}
      size = long(data['size'])
    else:
      checksum = None
      attributes = None
      size = None
      
    return fs_file_info(file_util.lstrip_sep(remote_filename), ftype, size, checksum, attributes, fs_file_info_list())

  def _make_entry(self, remote_filename, entry, children):
    if 'children' in entry:
      ftype = fs_file_info.DIR
    else:
      ftype = fs_file_info.FILE
    if ftype == fs_file_info.FILE:
      checksum = str(entry['sha2'])
      attributes = {}
      size = entry['size']
    else:
      checksum = None
      attributes = None
      size = None
    return fs_file_info(file_util.lstrip_sep(remote_filename), ftype, size, checksum, attributes, children)

  #@abstractmethod
  def remove_file(self, filename):
    'Remove filename.'
    assert False
    
  #@abstractmethod
  def upload_file(self, filename, local_filename):
    'Upload filename from local_filename.'
    assert False

  #@abstractmethod
  def download_file(self, filename, local_filename):
    'Download filename to local_filename.'
    assert False
    
  #@abstractmethod
  def set_file_attributes(self, filename, attributes):
    'Set file attirbutes.'
    assert False

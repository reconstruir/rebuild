#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from os import path
import json

import requests

from bes.common.check import check
from bes.common.node import node
from bes.fs.file_attributes import file_attributes
from bes.fs.file_checksum import file_checksum
from bes.fs.file_checksum_db import file_checksum_db
from bes.fs.file_find import file_find
from bes.fs.file_metadata import file_metadata
from bes.fs.file_path import file_path
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
    remote_dir_no_leading_sep = file_util.lstrip_sep(remote_dir)
    artifactory_repo = remote_dir.split('/')[1]
    match_prefix = '/'.join(remote_dir.split('/')[2:])

    decomposed_path = file_path.decompose(remote_dir)
    
    #print('         address: {}'.format(self._address))
    #print('      remote_dir: {}'.format(remote_dir))
#    print(' decomposed_path: {}'.format(decomposed_path))
#    print(' decomposed_path len: {}'.format(len(decomposed_path)))
    #print('artifactory_repo: {}'.format(artifactory_repo))
    #print('    match_prefix: {}'.format(match_prefix))

    aql_url = '{address}/api/search/aql'.format(address = self._address)
    data = {
      'repo': artifactory_repo,
      "path" : {
        '$match': '{}*'.format(match_prefix),
      },
      'type': 'any',
    }
    if not recursive:
      data['depth'] = str(len(decomposed_path) + 1)
    data_json = json.dumps(data)
    aql_template = 'items.find({data_json}).include("*", "property.*")'
    aql = aql_template.format(data_json = data_json)
    
    #print('    aql:\n---------------\n{}\n-------------------------\n'.format(aql))
    
    auth = ( self._credentials.username, self._credentials.password )
    response = requests.post(aql_url, data = aql, auth = auth)
    response_data = response.json()
#    print(response_data)
    response_results = response_data.get('results', None)
    assert response_results

    #import pprint
    #print(pprint.pformat(response_results))
    #assert False
    
    files = []
    dirs = []
    for entry in response_results:
      remote_filename = '/'.join([ entry['repo'], entry['path'], entry['name'] ])
      parts = remote_filename.split('/')
      entry['_remote_filename'] = remote_filename
      entry['_parts'] = parts
      if entry['type'] == 'folder':
        dirs.append(entry)
      else:
        files.append(entry)

    dirs = sorted(dirs, key = lambda entry: len(entry['_parts']))
    files = sorted(files, key = lambda entry: entry['_remote_filename'])

    entries = dirs + files
    
    result = node('/')
    setattr(result, '_remote_filename', '/')
    setattr(result, '_is_file', False)
    root_entry = {
      'type': 'folder',
      '_remote_filename': '/',
      '_parts': [],
    }
    setattr(result, '_entry', root_entry)

    for p in decomposed_path:
      remote_filename = file_util.lstrip_sep(p)
      parts = remote_filename.split('/')
      new_node = result.ensure_path(parts)
      entry = {
        'type': 'folder',
        '_remote_filename': remote_filename,
        '_parts': parts,
      }
      setattr(new_node, '_entry', entry)
    
    for entry in entries:
      remote_filename = entry['_remote_filename']
      parts = remote_filename.split('/')
      new_node = result.ensure_path(parts)
      setattr(new_node, '_entry', entry)

    starting_node = result.find_child(lambda child: getattr(child, '_entry')['_remote_filename'] == remote_dir_no_leading_sep)
    assert starting_node
    fs_tree = self._convert_node_to_fs_tree(starting_node, depth = 0)
    return fs_tree

  def _convert_node_to_fs_tree(self, n, depth = 0):
    indent = ' ' * depth
    assert hasattr(n, '_entry')
    entry = getattr(n, '_entry')
    is_file = entry['type'] == 'file'
    if is_file:
      children = fs_file_info_list()
    else:
      children = fs_file_info_list([ self._convert_node_to_fs_tree(child, depth + 2) for child in n.children ])
    entry = self._make_info(entry, children)
    return entry
    
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
    rd = self._parse_remote_filename(remote_filename)
    storage_response = self._storage_query(rd)
    if 'children' in storage_response:
      ftype = fs_file_info.DIR
    else:
      ftype = fs_file_info.FILE
    if ftype == fs_file_info.FILE:
      file_data = self._aql_query_file(rd)
      attributes = self._parse_artifactory_properties(file_data.get('properties', None))
      checksum = file_data['sha256']
      size = long(file_data['size'])
    else:
      checksum = None
      attributes = None
      size = None
    return fs_file_info(file_util.lstrip_sep(remote_filename), ftype, size, checksum, attributes, fs_file_info_list())

  #@abstractmethod
  def _aql_query_file(self, rd):
    aql_url = '{address}/api/search/aql'.format(address = self._address)
    data = {
      'repo': rd.repo,
      "path" : {
        '$match': path.dirname(rd.prefix),
      },
      "name" : {
        '$match': path.basename(rd.prefix),
      },
      'type': 'any',
    }
    data_json = json.dumps(data)
    aql_template = 'items.find({data_json}).include("*", "property.*")'
    aql = aql_template.format(data_json = data_json)
    auth = ( self._credentials.username, self._credentials.password )
    response = requests.post(aql_url, data = aql, auth = auth)
    response_data = response.json()
    results = response_data.get('results', None)
    if not results:
      raise fs_error('file not found: {}'.format(rd.remote_filename))
    assert len(results) == 1
    return results[0]

  #@abstractmethod
  def _storage_query(self, rd):
    url = '{}/api/storage{}'.format(self._address, rd.remote_filename_sep)
    auth = ( self._credentials.username, self._credentials.password )
    response = requests.get(url, auth = auth)
    if response.status_code != 200:
      raise fs_error('file not found: {}'.format(remote_filename))
    response_data = response.json()
    return response_data
  
  def _get_file_properties(self, remote_filename):
    'Get just the properties for a file.'

    url = '{}/api/storage{}?properties'.format(self._address, remote_filename)
    auth = ( self._credentials.username, self._credentials.password )
    response = requests.get(url, auth = auth)
    if response.status_code != 200:
      raise fs_error('file not found: {}'.format(remote_filename))
    data = response.json()
    return data

  def _make_info(self, entry, children):
    is_file = entry['type'] != 'folder'
    remote_filename = entry['_remote_filename']
    
    if is_file:
      ftype = fs_file_info.FILE
    else:
      ftype = fs_file_info.DIR
      
    if ftype == fs_file_info.FILE:
      checksum = str(entry['sha256'])
      attributes = self._parse_artifactory_properties(entry.get('properties', None))
      size = entry['size']
    else:
      checksum = None
      attributes = None
      size = None
    return fs_file_info(file_util.lstrip_sep(remote_filename), ftype, size, checksum, attributes, children)

  _PROP_KEY_BLACKLIST = [
    'trash.',
  ]

  @classmethod
  def _prop_key_is_black_listed(clazz, key):
    for x in clazz._PROP_KEY_BLACKLIST:
      if key.startswith(x):
        return True
    return False
  
  @classmethod
  def _parse_artifactory_properties(clazz, properties):
    if not properties:
      return {}
    result = {}
    for prop in properties:
      key = prop['key']
      if not clazz._prop_key_is_black_listed(key):
        result[key] = prop.get('value', None)
    return result
  
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

  _parsed_remote_filename = namedtuple('_parsed_remote_filename', 'remote_filename, decomposed_path, remote_filename_sep, remote_filename_no_sep, repo, prefix')
  @classmethod
  def _parse_remote_filename(clazz, remote_filename):
    'Parse a remote_filename and return the artifactory specific parts such as repo and prefix.'
    remote_filename_sep = file_util.ensure_lsep(remote_filename)
    remote_filename_no_sep = file_util.lstrip_sep(remote_filename)
    repo = remote_filename.split('/')[0]
    prefix = '/'.join(remote_filename_sep.split('/')[2:])
    decomposed_path = file_path.decompose(remote_filename_sep)
    return clazz._parsed_remote_filename(remote_filename, decomposed_path, remote_filename_sep,
                                         remote_filename_no_sep, repo, prefix)

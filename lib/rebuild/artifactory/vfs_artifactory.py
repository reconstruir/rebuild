#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from datetime import datetime

from os import path
import json, pprint

import requests

from bes.common.check import check
from bes.common.node import node
from bes.fs.file_attributes import file_attributes
from bes.fs.file_checksum import file_checksum
from bes.fs.file_checksum_db import file_checksum_db
from bes.fs.file_find import file_find
from bes.fs.file_metadata import file_metadata
from bes.fs.file_path import file_path
from bes.system.log import logger
from bes.factory.factory_field import factory_field

from bes.vfs.vfs_base import vfs_base
from bes.vfs.vfs_file_info import vfs_file_info
from bes.vfs.vfs_file_info import vfs_file_info_list
from bes.vfs.vfs_error import vfs_error
from bes.vfs.vfs_path_util import vfs_path_util

from rebuild.credentials.credentials import credentials

class vfs_artifactory(vfs_base):
  'artifactory filesystem'

  log = logger('fs')
  
  def __init__(self, config_source, address, credentials, cache_dir = None):
    check.check_string(config_source)
    check.check_string(address)
    check.check_credentials(credentials)
    check.check_string(cache_dir, allow_none = True)
    
    self._config_source = config_source
    self._address = address
    self._credentials = credentials
    self._cache_dir = cache_dir or path.expanduser('~/.besfs/vfs_artifactory/cache')

  def __str__(self):
    return 'vfs_artifactory({}@{})'.format(str(self._credentials), self._address)

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
  def create(clazz, config_source, **values):
    'Create an vfs_artifactory instance.'
    cred = credentials(config_source,
                       username = values['artifactory_username'],
                       password = values['artifactory_password'])
    return vfs_artifactory(config_source,
                          values['artifactory_address'],
                          cred,
                          cache_dir = values['artifactory_cache_dir'])
    
  @classmethod
  #@abstractmethod
  def name(clazz):
    'The name if this fs.'
    return 'vfs_artifactory'

  #@abstractmethod
  def list_dir(self, remote_dir, recursive):
    'List entries in a directory.'
    rd = self._parse_remote_filename(remote_dir)
    aql_response = self._aql_query_dir(rd, recursive)

    files = []
    dirs = []
    for entry in aql_response:
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

    result = node('/')
    setattr(result, '_remote_filename', '/')
    setattr(result, '_is_file', False)
    setattr(result, '_entry', self._make_entry('folder', '/', []))

    entries = dirs + files
    for p in rd.decomposed_path:
      remote_filename = vfs_path_util.lstrip_sep(p)
      parts = remote_filename.split('/')
      new_node = result.ensure_path(parts)
      setattr(new_node, '_entry', self._make_entry('folder', remote_filename, parts))
    
    for entry in entries:
      remote_filename = entry['_remote_filename']
      parts = remote_filename.split('/')
      new_node = result.ensure_path(parts)
      setattr(new_node, '_entry', entry)

    starting_node = result.find_child(lambda child: getattr(child, '_entry')['_remote_filename'] == rd.remote_filename_no_sep)
    assert starting_node
    fs_tree = self._convert_node_to_fs_tree(starting_node, depth = 0)
    return fs_tree

  @classmethod
  def _make_entry(clazz, etype, remote_filename, parts):
    return {
      'type': etype,
      '_remote_filename': remote_filename,
      '_parts': parts,
    }
  
  def _convert_node_to_fs_tree(self, n, depth = 0):
    indent = ' ' * depth
    assert hasattr(n, '_entry')
    entry = getattr(n, '_entry')
    is_file = entry['type'] == 'file'
    if is_file:
      children = vfs_file_info_list()
    else:
      children = vfs_file_info_list([ self._convert_node_to_fs_tree(child, depth + 2) for child in n.children ])
    entry = self._make_info(entry, children)
    return entry
    
  #@abstractmethod
  def has_file(self, remote_filename):
    'Return True if filename exists in the filesystem and is a FILE.'
    try:
      self.file_info(remote_filename)
      return True
    except vfs_error as ex:
      return False

  #@abstractmethod
  def file_info(self, remote_filename):
    'Get info for a single file.'
    rd = self._parse_remote_filename(remote_filename)
    storage_response = self._storage_query(rd)
    last_modified = storage_response['lastModified']
    modification_date = datetime.strptime(last_modified, "%Y-%m-%dT%H:%M:%S.%fZ")
    if 'children' in storage_response:
      ftype = vfs_file_info.DIR
    else:
      ftype = vfs_file_info.FILE
    if ftype == vfs_file_info.FILE:
      file_data = self._aql_query_file(rd)
      attributes = self._parse_artifactory_properties(file_data.get('properties', None))
      checksum = file_data['sha256']
      size = long(file_data['size'])
    else:
      checksum = None
      attributes = None
      size = None
    return vfs_file_info(vfs_path_util.dirname(remote_filename),
                         vfs_path_util.basename(remote_filename),
                         ftype,
                         modification_date,
                         size,
                         checksum,
                         attributes)

  #@abstractmethod
  def _aql_query_dir(self, rd, recursive):
    aql_url = '{address}/api/search/aql'.format(address = self._address)
    data = {
      'repo': rd.repo,
      "path" : {
        '$match': '{}*'.format(rd.prefix),
      },
      'type': 'any',
    }
    if not recursive:
      data['depth'] = str(len(rd.decomposed_path))
    
    data_json = json.dumps(data)
    aql_template = 'items.find({data_json}).include("*", "property.*")'
    aql = aql_template.format(data_json = data_json)
    self.log.log_d('_aql_query_dir: aql={}'.format(aql))
    auth = ( self._credentials.username, self._credentials.password )
    response = requests.post(aql_url, data = aql, auth = auth)
    response_data = response.json()
    self.log.log_d('_aql_query_dir: response_data={}'.format(pprint.pformat(response_data)))
    results = response_data.get('results', None)
    if not results:
      raise vfs_error('file not found: {}'.format(rd.remote_filename))
    return results

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
      raise vfs_error('file not found: {}'.format(rd.remote_filename))
    assert len(results) == 1
    return results[0]

  #@abstractmethod
  def _storage_query(self, rd):
    url = '{}/api/storage{}'.format(self._address, rd.remote_filename_sep)
    auth = ( self._credentials.username, self._credentials.password )
    response = requests.get(url, auth = auth)
    if response.status_code != 200:
      raise vfs_error('file not found: {}'.format(rd.remote_filename))
    response_data = response.json()
    return response_data
  
  def _get_file_properties(self, remote_filename):
    'Get just the properties for a file.'

    url = '{}/api/storage{}?properties'.format(self._address, remote_filename)
    auth = ( self._credentials.username, self._credentials.password )
    response = requests.get(url, auth = auth)
    if response.status_code != 200:
      raise vfs_error('file not found: {}'.format(remote_filename))
    data = response.json()
    return data

  def _make_info(self, entry, children):
    is_file = entry['type'] != 'folder'
    remote_filename = entry['_remote_filename']
    
    if is_file:
      ftype = vfs_file_info.FILE
    else:
      ftype = vfs_file_info.DIR
    if ftype == vfs_file_info.FILE:
      checksum = str(entry['sha256'])
      attributes = self._parse_artifactory_properties(entry.get('properties', None))
      size = entry['size']
    else:
      checksum = None
      attributes = None
      size = None
    if not 'modified' in entry:
      print('BAD ENTRY: {}'.format(pprint.pformat(entry)))
      modification_date = datetime.now()
    else:
      modified = entry['modified']
      modification_date = datetime.strptime(modified, "%Y-%m-%dT%H:%M:%S.%fZ")
    return vfs_file_info(vfs_path_util.dirname(remote_filename),
                         vfs_path_util.basename(remote_filename),
                         ftype,
                         modification_date,
                         size,
                         checksum,
                         attributes,
                         children)

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
####    with open(local_filename, 'rb') as fin:
####      response = requests.put(url,
####                              auth = ( credentials.username, credentials.password ),
####                              data = fin,
####                              headers = headers)
####      clazz.log.log_d('_do_upload_url: response status_code=%d' % (response.status_code))
####      if response.status_code != 201:
####        msg = 'Failed to upload: {} (status_code {} content {})'.format(url, response.status_code, response.content)
####        raise artifactory_error(msg, response.status_code, response.content)
####      data = response.json()
####      assert 'downloadUri' in data
####      return data['downloadUri']
####
####    
####    '''
####  @classmethod
####  def _do_upload_url(clazz, url, filename, credentials):
####    clazz.log.log_d('_do_upload_url: url=%s; filename=%s' % (url, filename))
####    import requests
####    headers = clazz.checksum_headers_for_file(filename)
####
####    '''
####    old_checksums = clazz.get_checksums_for_url(url, credentials)
####    if old_checksums:
####      new_sha256 = headers[clazz._HEADER_CHECKSUM_SHA256]
####      if old_checksums.sha256 == new_sha256:
####        clazz.log.log_i('_do_upload_url: url exists with same checksum.  doing nothing: {}'.format(url))
####        return url
####      msg = 'Trying to re-upload artifact with different checksum:\nfilename={}\nurl={}'.format(filename, url)
####      raise artifactory_error(msg, None, None)
####'''
####    
####    with open(filename, 'rb') as fin:
####      response = requests.put(url,
####                              auth = ( credentials.username, credentials.password ),
####                              data = fin,
####                              headers = headers)
####      clazz.log.log_d('_do_upload_url: response status_code=%d' % (response.status_code))
####      if response.status_code != 201:
####        msg = 'Failed to upload: {} (status_code {} content {})'.format(url, response.status_code, response.content)
####        raise artifactory_error(msg, response.status_code, response.content)
####      data = response.json()
####      assert 'downloadUri' in data
####      return data['downloadUri']
####    assert False
####'''

  #@abstractmethod
  def download_to_file(self, remote_filename, local_filename):
    'Download filename to local_filename.'
    assert False
    
  #@abstractmethod
  def download_to_bytes(self, remote_filename):
    'Download filename to bytes.'
    assert False
    
  #@abstractmethod
  def set_file_attributes(self, filename, attributes):
    'Set file attirbutes.'
    assert False

  _parsed_remote_filename = namedtuple('_parsed_remote_filename', 'remote_filename, decomposed_path, remote_filename_sep, remote_filename_no_sep, repo, prefix, url')
  def _parse_remote_filename(self, remote_filename):
    'Parse a remote_filename and return the artifactory specific parts such as repo and prefix.'
    remote_filename_sep = vfs_path_util.ensure_lsep(remote_filename)
    remote_filename_no_sep = vfs_path_util.lstrip_sep(remote_filename)
    repo = remote_filename_no_sep.split('/')[0]
    prefix = '/'.join(remote_filename_sep.split('/')[2:])
    decomposed_path = file_path.decompose(remote_filename_sep)
    return self._parsed_remote_filename(remote_filename, decomposed_path, remote_filename_sep,
                                        remote_filename_no_sep, repo, prefix, 'foo')

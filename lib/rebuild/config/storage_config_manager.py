#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import re

from bes.system.check import check
from bes.files.bf_temp_file import bf_temp_file

from bes.bconfig.bconfig import bconfig
from bes.bconfig.bconfig_error import bconfig_error

from .storage_config import storage_config
from .storage_config_error import storage_config_error

_ENV_VAR_RE = re.compile(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}')

class storage_config_manager(object):
  '''
  A named collection of storage_config entries.

  Two input shapes, same as before this moved off bat_config_file:
  - text/file: real, standalone TOML, a "[[storage]]" array of tables,
    read via bes.bconfig.
  - node: a bes.common.node subtree whose children are "storage"
    sections in the old indented "key: value" shape -- this is what
    rebuild.venv.venv_project_config_parser hands in, since its own
    ".revenv" recipe format is a completely different, unrelated
    tree_text_parser-based DSL that embeds a "config" section built the
    same low-level way. Migrating that embedding to TOML would mean
    migrating venv_project_config's entire recipe format, out of scope
    here -- so this path keeps reading the embedded node directly,
    without any bat_config_file dependency.
  '''

  error = storage_config_error

  def __init__(self, config, source):
    check.check_string(source)
    self.source = source
    self._configs = {}

    if check.is_string(config):
      all_values = self._parse_text(config, source)
    elif check.is_node(config):
      all_values = self._parse_node(config)
    else:
      raise TypeError('Unknown config type: %s\nShould be string or node: %s - %s' % (source, str(config), type(config)))
    for values in all_values:
      sc = storage_config.create_from_config(source, values)
      if sc.name in self._configs:
        raise self.error('storage with name "{}" already exists.'.format(sc.name))
      self._configs[sc.name] = sc

  def get(self, name):
    return self._configs.get(name, None)

  def available_configs(self):
    return sorted(self._configs.keys())

  @classmethod
  def from_file(clazz, filename):
    return storage_config_manager(filename, source = filename)

  @classmethod
  def from_text(clazz, text, source = None):
    return storage_config_manager(text, source = source)

  @classmethod
  def make_local_config(clazz, name, location, repo, root_dir):
    content = clazz.make_local_config_content(name, location, repo, root_dir)
    return clazz.from_text(content, source = '<default>')

  @classmethod
  def make_local_config_content(clazz, name, location, repo, root_dir):
    check.check_string(name)
    check.check_string(location)
    check.check_string(repo, allow_none = True)
    check.check_string(root_dir, allow_none = True)
    template = '''\
[[storage]]
name = {name}
provider = "local"
location = {location}
repo = {repo}
root_dir = {root_dir}
'''
    content = template.format(name = _toml_string(name),
                              location = _toml_string(location),
                              repo = _toml_string(repo or ''),
                              root_dir = _toml_string(root_dir or ''))
    return content

  @classmethod
  def _parse_text(clazz, text, source):
    tmp = bf_temp_file.make_temp_file(content = text, suffix = '.storage.toml')
    try:
      cfg = bconfig(tmp)
    except bconfig_error as ex:
      raise storage_config_error(f'{source}: {ex}') from ex
    return cfg.to_dict().get('storage', [])

  @classmethod
  def _parse_node(clazz, config_node):
    'Read a bat_config_file-shaped "storage" section directly from a node -- see class docstring.'
    result = []
    for storage_node in config_node.children:
      if storage_node.data.text != 'storage':
        continue
      values = {}
      for entry_node in storage_node.children:
        key, delimiter, value = entry_node.data.text.partition(':')
        if delimiter != ':':
          raise storage_config_error(f'invalid config entry (missing colon): "{entry_node.data.text}"')
        key = key.strip()
        if not key:
          raise storage_config_error(f'invalid config entry (empty key): "{entry_node.data.text}"')
        values[key] = clazz._substitute_env_vars(value.strip())
      result.append(values)
    return result

  @classmethod
  def _substitute_env_vars(clazz, value):
    def _substitute(match):
      var_name = match.group(1)
      if var_name not in os.environ:
        raise storage_config_error(f'environment variable not set: "{var_name}"')
      return os.environ[var_name]
    return _ENV_VAR_RE.sub(_substitute, value)

def _toml_string(value):
  return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'

check.register_class(storage_config_manager, include_seq = False)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from bes.common.check import check
from bes.common.json_util import json_util
from bes.common.string_util import string_util
from rebuild.base import requirement_list

class sql_encoding(object):

  @classmethod
  def encode_string(clazz, s, quoted = True):
    if s is None:
      return 'null'
    if quoted:
      return string_util.quote(s, quote_char = "'")
    return s

  @classmethod
  def encode_string_list(clazz, l, quoted = True):
    check.check_string_seq(l)
    return clazz.encode_string(json_util.to_json(l), quoted = quoted)
  
  @classmethod
  def encode_requirements(clazz, reqs):
    check.check_requirement_list(reqs)
    return clazz.encode_string_list(reqs.to_string_list())

  @classmethod
  def decode_requirements(clazz, text):
    return requirement_list.from_string_list(json.loads(text))
  
  def decode_string_list(clazz, text):
    return string_list.parse(text)
  
  @classmethod
  def encode_dict(clazz, d):
    return clazz.encode_string(json_util.to_json(d, sort_keys = True))

  @classmethod
  def encode_files(clazz, files):
    return clazz.encode_string(json_util.to_json(files.to_simple_list()))

  @classmethod
  def decode_arch(clazz, arch):
    check.check_string(arch)
    return tuple(json.loads(arch))

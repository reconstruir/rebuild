#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from bes.common import check, json_util, string_util
from rebuild.base import requirement_list

class sql_encoding(object):

  @classmethod
  def sql_encode_string(clazz, s, quoted = True):
    if s is None:
      return 'null'
    if quoted:
      return string_util.quote(s, quote_char = "'")
    return s

  @classmethod
  def sql_encode_string_list(clazz, l, quoted = True):
    check.check_string_seq(l)
    return clazz.sql_encode_string(json_util.to_json(l), quoted = quoted)
  
  @classmethod
  def sql_encode_requirements(clazz, reqs):
    check.check_requirement_list(reqs)
    return clazz.sql_encode_string_list(reqs.to_string_list())

  @classmethod
  def sql_decode_requirements(clazz, text):
    return requirement_list.from_string_list(json.loads(text))
  
  @classmethod
  def sql_encode_dict(clazz, d):
    return clazz.sql_encode_string(json_util.to_json(d, sort_keys = True))

  @classmethod
  def sql_encode_files(clazz, files):
    return clazz.sql_encode_string(json_util.to_json(files.to_simple_list()))

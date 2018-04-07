#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from bes.common import check, json_util, string_util
from bes.fs import file_checksum, file_checksum_list
from rebuild.base import requirement_list

class util(object):

  @classmethod
  def requirements_from_string_list(clazz, l):
    check.check_string_seq(l)
    result = requirement_list()
    for n in l:
      result.extend(requirement_list.parse(n))
    return result

  @classmethod
  def requirements_to_string_list(clazz, reqs):
    check.check_requirement_list(reqs)
    return [ str(r) for r in reqs ]

  @classmethod
  def sql_encode_string(clazz, s, quoted = True):
    if s is None:
      return 'null'
    if quoted:
      return string_util.quote(s, quote_char = "'")
    return s

  @classmethod
  def sql_encode_string_list(clazz, l, quoted = True):
    return clazz.sql_encode_string(json_util.to_json(l), quoted = quoted)
  
  @classmethod
  def sql_encode_requirements(clazz, reqs):
    return clazz.sql_encode_string_list(clazz.requirements_to_string_list(reqs))

  @classmethod
  def sql_decode_requirements(clazz, text):
    return clazz.requirements_from_string_list(json.loads(text))
  
  @classmethod
  def sql_encode_dict(clazz, d):
    return clazz.sql_encode_string(json_util.to_json(d, sort_keys = True))

  @classmethod
  def sql_encode_files(clazz, files):
    return clazz.sql_encode_string(json_util.to_json(files.to_simple_list()))

  @classmethod
  def files_from_sql_rows(clazz, rows):
    result = file_checksum_list()
    for row in rows:
      result.append(file_checksum(row.filename, row.checksum))
    return result

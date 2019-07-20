#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.key_value.key_value_list import key_value_list

from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.masked_value_list import masked_value_list
from rebuild.recipe.value.value_key_values import value_key_values

from .ingest_method_descriptor_http import ingest_method_descriptor_http
from .ingest_method_descriptor_git import ingest_method_descriptor_git

from .ingest_method import ingest_method

class ingest_unit_test(object):

  @classmethod
  def make_ingest_method(clazz, method, url = None, checksum = None, ingested_filename = None):
    method = method or 'download'
    url = url or 'http://www.examples.com/foo.zip'
    checksum = checksum or 'chk'
    ingested_filename = ingested_filename or 'foo.zop'
    values = masked_value_list([
      masked_value('all', value_key_values(value = key_value_list.parse('url={}'.format(url)))),
      masked_value('all', value_key_values(value = key_value_list.parse('checksum={}'.format(checksum)))),
      masked_value('all', value_key_values(value = key_value_list.parse('ingested_filename={}'.format(ingested_filename)))),
    ])

    if method == 'git':
      desc = ingest_method_descriptor_git()
    elif method == 'download':
      desc = ingest_method_descriptor_http()
    else:
      raise RuntimeError('invalid method: {} - should be one of: git download'.format(method))
    
    return ingest_method(desc, values)

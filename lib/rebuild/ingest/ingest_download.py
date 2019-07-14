#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.system.log import log

from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.masked_value_list import masked_value_list

class ingest_download(namedtuple('ingest_download', 'url, git')):
  def __new__(clazz, url, git):
    check.check_masked_value_list(url, allow_none = True)
    check.check_masked_value_list(git, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, url, git)

check.register_class(ingest_download, include_seq = False)

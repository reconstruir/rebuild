# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.table import table
from bes.text.text_box import text_box_unicode, text_box_space
from bes.text.text_table import text_table
from bes.text.text_table import text_table, text_cell_renderer, text_table_style
from bes.version.version import version

class rebuild_module_versions(object):

  @classmethod
  def module_versions(clazz):
    return version.module_versions([
      'bes',
      'gitlab',
    ])

  @classmethod
  def format_module_versions(clazz, versions, fancy = False, filenames = False):
    if fancy:
      style = text_table_style(spacing = 1, box = text_box_unicode())
    else:
      style = text_table_style(spacing = 1, box = text_box_space())
    items = sorted(versions.values())
    data = table(data = items)
    if not filenames:
      data.remove_column(2)
    tt = text_table(data = data, style = style)
    if filenames:
      tt.set_labels( ( 'NAME', 'VERSION', 'FILENAME' ) )
    else:
      tt.set_labels( ( 'NAME', 'VERSION' ) )
    return str(tt)

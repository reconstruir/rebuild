#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, sys
from bes.common.json_util import json_util
from bes.system.add_method import add_method
from bes.system.console import console
from bes.fs.file_util import file_util
from bes.text.text_fit import text_fit

class build_blurb(object):

  DEFAULT_LABEL_LENGTH = 12

  CONFIG_FILENAME = path.expanduser('~/.bes_blurb_config')
#  DEFAULT_CONFIG = { 'label_length': 10 }

  _label_length = None
  _process_name = None

  verbose = False

  @classmethod
  def set_verbose(clazz, verbose):
    clazz.verbose = verbose

  @classmethod
  def blurb(clazz, label, message, output = sys.stdout, fit = False):
    assert label
    justified_label = clazz.justified_label(label)
    delimiter = ': '
    left_width = len(justified_label) + len(delimiter)
    output.write(justified_label)
    output.write(delimiter)
    lines = []
    if fit:
      terminal_width = console.terminal_width(default = 80)
      width = terminal_width - left_width
      if len(message) > width:
        lines = text_fit.fit_text(message, width)
    if lines:
      for i, line in enumerate(lines):
        if i != 0:
          output.write('\n')
          output.write(' ' * left_width)
        output.write(line)
        first = False
    else:
      output.write(message)
    output.write('\n')
    output.flush()

  @classmethod
  def blurb_verbose(clazz, label, message, output = sys.stdout, fit = False):
    if not clazz.verbose:
      return
    clazz.blurb(label, message, output = output, fit = fit)

  @classmethod
  def justified_label(clazz, label):
    return label.rjust(12) #self.__get_label_length())

  @staticmethod
  def _transplant_blurb(obj, message, output = sys.stdout, fit = False):
    assert getattr(obj, 'rebuild_blurb_label__', None) != None
    build_blurb.blurb(obj.rebuild_blurb_label__, message, output = output, fit = fit)

  @staticmethod
  def _transplant_blurb_verbose(obj, message, output = sys.stdout, fit = False):
    assert getattr(obj, 'rebuild_blurb_verbose_label__', None) != None
    build_blurb.blurb_verbose(obj.rebuild_blurb_verbose_label__, message, output = output, fit = fit)

  @classmethod
  def add_blurb(clazz, obj, label = None):
    'Add blubing capabilities to obj.'
    if type(obj) == type:
      object_class = obj
    else:
      object_class = obj.__class__

    if getattr(object_class, 'rebuild_blurb_label__', False):
      return
      
    if getattr(object_class, 'blurb', None):
      raise RuntimeError('class already has a blurb method: %s' % (object_class))

    label = label or object_class.__class__.__name__
    add_method(clazz._transplant_blurb, object_class, 'blurb')
    setattr(object_class, 'rebuild_blurb_label__', label)

    add_method(clazz._transplant_blurb_verbose, object_class, 'blurb_verbose')
    setattr(object_class, 'rebuild_blurb_verbose_label__', label)
    
  @classmethod
  def set_process_name(clazz, process_name):
    'Set the global name for the current process.  Used to know what key to use for persistent settings.'
    clazz._process_name = process_name

  @classmethod
  def __load_config(clazz):
    'Load blurb config from disk.'
    o = json_util.read_file(clazz.CONFIG_FILENAME)
    if not o:
      return DEFAULT_CONFIG
    assert 'label_length' in o
    return o

  @classmethod
  def __save_config(clazz, config):
    'Load blurb config from disk.'
    json_util.save_file(clazz.CONFIG_FILENAME, config, indent = 2)

  @classmethod
  def __get_label_length(clazz):

    DEFAULT_LABEL_LENGTH

    if clazz._label_length == None:
      config = clazz.__load_config()
      clazz._label_length = int(config['label_length'])
      assert clazz._label_length > 0
      assert clazz._label_length < 100
    return clazz._label_length

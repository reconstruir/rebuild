#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class native_package_error(Exception):
  def __init__(self, message, status_code = None):
    super(native_package_error, self).__init__()
    self.message = message
    self.status_code = status_code

  def __str__(self):
    return self.message

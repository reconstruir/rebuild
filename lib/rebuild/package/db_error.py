#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class NotInstalledError(Exception):

  def __init__(self, message, what):
    super(NotInstalledError, self).__init__(message)
    self.message = message
    self.what = what

  def __str__(self):
    return self.message

class AlreadyInstalledError(Exception):

  def __init__(self, message, what):
    super(AlreadyInstalledError, self).__init__(message)
    self.message = message
    self.what = what

  def __str__(self):
    return self.message
  

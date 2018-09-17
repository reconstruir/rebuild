#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class error(Exception):

  LOG_IN_REQUIRED = 1000
  PARENT_DIR_MISSING = 2002
  
  CODES = {
    LOG_IN_REQUIRED: 'Log in required.',
    1004: 'No fileid or path provided.',
    2000: 'Log in failed.',
    PARENT_DIR_MISSING: 'A component of parent directory does not exist.',
    2003: 'Access denied. You do not have permissions to preform this operation.',
    2009: 'File not found.',
    2010: 'Invalid path.',
    4000: 'Too many login tries from this IP address.',
    5000: 'Internal error. Try again later.',
  }
  
  def __init__(self, code):
    assert code in self.CODES
    message = self.CODES[code]
    super(error, self).__init__(message)
    self.message = message
    self.code = code

  def __str__(self):
    return '{message} - {code}'.format(message = self.message, code = self.code)

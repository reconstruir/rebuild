#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class pcloud_error(Exception):

  LOG_IN_REQUIRED = 1000
  PARENT_DIR_MISSING = 2002
  ALREADY_EXISTS = 2004
  
  CODES = {
    1004: 'No fileid or path provided.',
    2000: 'Log in failed.',
    2003: 'Access denied. You do not have permissions to preform this operation.',
    2005: 'Directory does not exist.',
    2009: 'File not found.',
    2010: 'Invalid path.',
    4000: 'Too many login tries from this IP address.',
    5000: 'Internal error. Try again later.',
    ALREADY_EXISTS: 'File or folder alredy exists.',
    LOG_IN_REQUIRED: 'Log in required.',
    PARENT_DIR_MISSING: 'A component of parent directory does not exist.',
  }
  
  def __init__(self, code, what):
    assert code in self.CODES
    message = self.CODES[code]
    super(pcloud_error, self).__init__(message)
    self.what = what
    self.message = message
    self.code = code

  def __str__(self):
    return '{message}: {what} ({code})'.format(message = self.message, what = self.what, code = self.code)

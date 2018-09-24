#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class pcloud_error(Exception):

  LOG_IN_REQUIRED = 1000
  PARENT_DIR_MISSING = 2002
  ALREADY_EXISTS = 2004
  HTTP_ERROR = 9999
  
  CODES = {
    1001: 'No full path or name/folderid provided.',
    1002: 'No full path or folderid provided.',
    1004: 'No fileid or path provided.',
    1006: 'Please provide flags.',
    1007: 'Invalid or closed file descriptor.',
    2000: 'Log in failed.',
    2001: 'Invalid file/folder name.',
    2003: 'Access denied. You do not have permissions to preform this operation.',
    2005: 'Directory does not exist.',
    2006: 'Folder is not empty.',
    2007: 'Cannot delete the root folder.',
    2008: 'User is over quota.',
    2009: 'File not found.',
    2010: 'Invalid path.',
    2028: 'There are active shares or sharerequests for this folder.',
    4000: 'Too many login tries from this IP address.',
    5000: 'Internal error. Try again later.',
    5001: 'Internal upload error.',
    HTTP_ERROR: 'HTTP error.',
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

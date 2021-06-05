# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class rebuild_depends_cli_args(object):

  def depends_add_args(self, parser):
    parser.add_argument('-f', '--filenames', action = 'store_true', default = False,
                        help = 'Print filenames where the modules where imported from. [ False ]')
    parser.add_argument('-p', '--plain', action = 'store_true', default = False,
                        help = 'Use plain formatting instead of a fancy table. [ False ]')
  
  def _command_depends(self, command, *args, **kargs):
    assert command == None
    assert 'filenames' in kargs
    assert 'plain' in kargs
    from .rebuild_module_versions import rebuild_module_versions
    versions = rebuild_module_versions.module_versions()
    s = rebuild_module_versions.format_module_versions(versions,
                                                   fancy = not kargs['plain'],
                                                   filenames = kargs['filenames'])
    print(s)
    return 0

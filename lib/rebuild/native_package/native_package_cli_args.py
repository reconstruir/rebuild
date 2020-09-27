#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class native_package_cli_args(object):

  def __init__(self):
    pass
  
  def native_package_add_args(self, subparser):

    # list
    p = subparser.add_parser('list', help = 'List installed packages.')

    # installed
    p = subparser.add_parser('installed', help = 'Check if pacakge_name is installed')
    p.add_argument('package_name', action = 'store', help = 'The package name')

    # info
    p = subparser.add_parser('info', help = 'Print platform specific info about package')
    p.add_argument('package_name', action = 'store', help = 'The package name')

    # files
    p = subparser.add_parser('files', help = 'Print package files')
    p.add_argument('package_name', action = 'store', help = 'The package name')
    p.add_argument('--levels', '-l', action = 'store', type = int,
                   default = None, help = 'Show only top level directories [ None ]')

    # dirs
    p = subparser.add_parser('dirs', help = 'Print package dirs')
    p.add_argument('package_name', action = 'store', help = 'The package name')
    p.add_argument('--levels', '-l', action = 'store', type = int,
                   default = None, help = 'Show only top level directories [ None ]')
    
    # owner
    p = subparser.add_parser('owner', help = 'Print the package the owns the given file.')
    p.add_argument('filename', action = 'store', help = 'The filename')

    # remove
    p = subparser.add_parser('remove', help = 'remove a package')
    p.add_argument('package_name', action = 'store', help = 'The package name')
    p.add_argument('--force-package-root', action = 'store_true',
                   default = False, help = 'Force removal of the package root directory even if not empty [ False ]')
    
  def _command_native_package(self, command, *args, **kargs):
    from .native_package_cli_command import native_package_cli_command
    return native_package_cli_command.handle_command(command, **kargs)

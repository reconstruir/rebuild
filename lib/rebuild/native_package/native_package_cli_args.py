#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class native_package_cli_args(object):

  def __init__(self):
    pass
  
  def native_package_add_args(self, subparser):

    # list
    p = subparser.add_parser('list', help = 'List installed packages.')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')

    # installed
    p = subparser.add_parser('installed', help = 'Check if package_name is installed')
    p.add_argument('package_name', action = 'store', help = 'The package name')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')

    # info
    p = subparser.add_parser('info', help = 'Print platform specific info about package')
    p.add_argument('package_name', action = 'store', help = 'The package name')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')

    # files
    p = subparser.add_parser('files', help = 'Print package files')
    p.add_argument('package_name', action = 'store', help = 'The package name')
    p.add_argument('--levels', '-l', action = 'store', type = int,
                   default = None, help = 'Show only top level directories [ None ]')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')

    # dirs
    p = subparser.add_parser('dirs', help = 'Print package dirs')
    p.add_argument('package_name', action = 'store', help = 'The package name')
    p.add_argument('--levels', '-l', action = 'store', type = int,
                   default = None, help = 'Show only top level directories [ None ]')
    p.add_argument('--root-dir', action = 'store_true', 
                   default = False, help = 'Show only the root dir [ None ]')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')
    
    # owner
    p = subparser.add_parser('owner', help = 'Print the package the owns the given file.')
    p.add_argument('filename', action = 'store', help = 'The filename')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')

    # remove
    p = subparser.add_parser('remove', help = 'Remove a package')
    p.add_argument('package_name', action = 'store', help = 'The package name')
    p.add_argument('--force-package-root', action = 'store_true',
                   default = False, help = 'Force removal of the package root directory even if not empty [ False ]')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')

    # install
    p = subparser.add_parser('install', help = 'Install a package')
    p.add_argument('package_filename', action = 'store', help = 'The package file')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   default = False, help = 'Verbose output')
    
  def _command_native_package(self, command, *args, **kargs):
    from .native_package_cli_command import native_package_cli_command
    return native_package_cli_command.handle_command(command, **kargs)

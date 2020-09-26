#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class native_package_cli_args(object):

  def __init__(self):
    pass
  
  def native_package_add_args(self, subparser):

    # list
    p = subparser.add_parser('list', help = 'List installed packages.')

    p = subparser.add_parser('installed', help = 'Check if pacakge_name is installed')
    p.add_argument('package_name', action = 'store', help = 'The package name')

    p = subparser.add_parser('info', help = 'Print platform specific info about package')
    p.add_argument('package_name', action = 'store', help = 'The package name')

    p = subparser.add_parser('contents', help = 'Print package contents')
    p.add_argument('package_name', action = 'store', help = 'The package name')
    p.add_argument('--levels', '-l', action = 'store', type = int,
                   default = None, help = 'Show only top level directories [ None ]')
    p.add_argument('--files', dest = 'files_only', action = 'store_true',
                   default = False, help = 'Show only files (no dirs) [ False ]')
    p.add_argument('--dirs', dest = 'dirs_only', action = 'store_true',
                   default = False, help = 'Show only dirs (no files) [ False ]')

    p = subparser.add_parser('owner', help = 'Print the package the owns the given file.')
    p.add_argument('filename', action = 'store', help = 'The filename')
    
  def _command_native_package(self, command, *args, **kargs):
    from .native_package_cli_command import native_package_cli_command
    return native_package_cli_command.handle_command(command, **kargs)

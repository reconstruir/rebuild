#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class archive_cli_args(object):

  def __init__(self):
    pass
  
  def archive_add_args(self, subparser):

    import os
    default_root = os.getcwd()
    default_format = 'zip'
    
    # create
    p = subparser.add_parser('create_git', help = 'Create an archive from a git repo.')
    p.add_argument('prefix', action = 'store', default = None,
                   help = 'The prefix inside the archive (ie  foo-1.2.3/) [ None ]')
    p.add_argument('revision', action = 'store', default = None,
                   help = 'The git revision to archive. [ None ]')
    p.add_argument('output_filename', action = 'store', default = None,
                   help = 'The output filename. [ None ]')
    p.add_argument('--root-dir', action = 'store', default = default_root,
                   help = 'The root dir of the git repo to archive. [ None ]')
    p.add_argument('--format', action = 'store', default = default_format,
                   choices = ( 'zip', 'tgz' ), dest = 'archive_format',
                   help = 'The format of the exported archive (zip or tgz) [ zip ]')
    
    # remove_members
    p = subparser.add_parser('remove_members', help = 'Remove members from the archive.')
    p.add_argument('archive_filename', action = 'store', default = None,
                   help = 'The archive filename [ None ]')
    p.add_argument('members', action = 'store', default = None, nargs = '+',
                   help = 'The members to remove. [ None ]')
    
    # contents
    p = subparser.add_parser('contents', help = 'Show the contents of an archive.')
    p.add_argument('archives', action = 'store', default = [], nargs = '+',
                   help = 'Archives to check for duplicates [ ]')
    
    # duplicates
    p = subparser.add_parser('duplicates', help = 'Show duplicates between archives contents.')
    p.add_argument('--check-content', action = 'store_true', default = False,
                   help = 'Check content checksums and only print those that are not the same between archives. [ False ]')
    p.add_argument('archives', action = 'store', default = [], nargs = '+',
                   help = 'Archives to check for duplicates [ ]')

    # extract
    default_dest_dir = os.getcwd()
    p = subparser.add_parser('extract', help = 'Extract archives.')
    p.add_argument('--dest-dir', action = 'store', default = default_dest_dir,
                   help = 'Destination dir where to extract archives. [ {} ]'.format(default_dest_dir))
    p.add_argument('archives', action = 'store', default = [], nargs = '+',
                   help = 'Archives to extract [ ]')

    # extract_file
    p = subparser.add_parser('extract_file', help = 'Extract files from archives.')
    p.add_argument('archive_filename', action = 'store', default = None,
                   help = 'The archive [ None ]')
    p.add_argument('filename', action = 'store', default = None,
                   help = 'The filename to extract [ None ]')
    p.add_argument('-o', '--output-filename', action = 'store', default = None,
                   help = 'The output filename [ None ]')
    
    # cat
    p = subparser.add_parser('cat', help = 'Cat a member file.')
    p.add_argument('archive_filename', action = 'store', default = None,
                   help = 'The archive [ None ]')
    p.add_argument('filename', action = 'store', default = None,
                   help = 'The filename to extract [ None ]')
    
    # combine
    p = subparser.add_parser('combine', help = 'Combine archives.')
    p.add_argument('dest_archive', action = 'store', default = None,
                   help = 'The destination archive [ ]')
    p.add_argument('archives', action = 'store', default = [], nargs = '+',
                   help = 'Archives to combine [ ]')
    p.add_argument('--check-content', action = 'store_true', default = False,
                   help = 'Check content checksums and only print those that are not the same between archives. [ False ]')
    p.add_argument('--base-dir', action = 'store', default = None,
                   help = 'Use the base dir for dest_archive. [ False ]')
    p.add_argument('--exclude', action = 'append', default = [],
                   help = 'Exclude the given member from both the content check and dest_archive. [ ]')

    # diff
    p = subparser.add_parser('diff', help = 'Diff content of 2 archives.')
    p.add_argument('archive1', action = 'store', default = None,
                   help = 'The first archive [ ]')
    p.add_argument('archive2', action = 'store', default = None,
                   help = 'The second archive [ ]')

    # diff_manifest
    p = subparser.add_parser('diff_manifest', help = 'Diff the manifest of 2 archives.')
    p.add_argument('archive1', action = 'store', default = None,
                   help = 'The first archive [ ]')
    p.add_argument('archive2', action = 'store', default = None,
                   help = 'The second archive [ ]')

    # diff_dir
    p = subparser.add_parser('diff_dir', help = 'Diff content of a dir of archives.')
    p.add_argument('dir1', action = 'store', default = None,
                   help = 'The first dir [ ]')
    p.add_argument('dir2', action = 'store', default = None,
                   help = 'The second dir [ ]')

    
    # search
    p = subparser.add_parser('search', help = 'Search for text in the archives contents.')
    p.add_argument('archive', action = 'store', default = None,
                   help = 'The archive [ ]')
    p.add_argument('text', action = 'store', default = None,
                   help = 'The text to search for [ ]')
    p.add_argument('-i', '--ignore-case', action = 'store_true', default = False,
                   help = 'Ignore case. [ ]')
    p.add_argument('-w', '--whole-word', action = 'store_true', default = False,
                   help = 'Only match whole words. [ ]')

  def _command_archive(self, command, *args, **kargs):
    from .archive_cli_command import archive_cli_command
    return archive_cli_command.handle_command(command, **kargs)

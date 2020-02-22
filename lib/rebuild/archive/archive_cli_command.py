#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.git.git_repo import git_repo
from bes.archive.archiver import archiver
from bes.archive.archive_util import archive_util

class archive_cli_command(object):
  
  @classmethod
  def create_git(clazz, root_dir, prefix, revision, output_filename, archive_format):
    r = git_repo(root_dir)
    r.archive_to_file(prefix, revision, output_filename,
                      archive_format = archive_format,
                      short_hash = True)
    return 0

  @classmethod
  def remove_members(clazz, archive, members):
    archive_util.remove_members(archive, members)
    return 0

  @classmethod
  def contents(clazz, archives):
    if len(archives) == 1:
      clazz._do_contents_one_archive(archives[0], False)
    else:
      for archive in archives:
        clazz._do_contents_one_archive(archive, True)
    return 0

  @classmethod
  def _do_contents_one_archive(clazz, archive, print_archive):
    for member in archiver.members(archive):
      if print_archive:
        print('{}:{}'.format(path.basename(archive), member))
      else:
        print(member)
  
  @classmethod
  def duplicates(clazz, archives, check_content):
    dups = archive_util.duplicate_members(archives, only_content_conficts = check_content)
    for member, archives in sorted(dups.items()):
      print('{}: {}'.format(member, ' '.join(archives)))
    return 0

  @classmethod
  def extract(clazz, archives, dest_dir):
    for archive in archives:
      archiver.extract_all(archive, dest_dir)
    return 0

  @classmethod
  def extract_file(clazz, archive, filename, output_filename):
    archiver.extract_member_to_file(archive, filename, output_filename)
    return 0

  @classmethod
  def cat(clazz, archive, filename):
    s = archiver.extract_member_to_string(archive, filename, codec = 'utf-8')
    print(s)
    return 0

  @classmethod
  def search(clazz, archive, what, ignore_case, whole_word):
    rv = archive_util.search(archive, what, ignore_case = ignore_case, whole_word = whole_word)
    print(rv.stdout)
    return rv.exit_code

  @classmethod
  def combine(clazz, dest_archive, archives, check_content, base_dir, exclude):
    archive_util.combine(archives, dest_archive,
                         check_content = check_content,
                         base_dir = base_dir,
                         exclude = exclude)
    return 0

  @classmethod
  def diff(clazz, archive1, archive2):
    rv = archive_util.diff_contents(archive1, archive2)
    print(rv.stdout)
    return rv.exit_code
  
  @classmethod
  def diff_manifest(clazz, archive1, archive2):
    rv = archive_util.diff_manifest(archive1, archive2)
    print(rv.stdout)
    return rv.exit_code

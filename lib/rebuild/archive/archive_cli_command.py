#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.git.git_repo import git_repo
from bes.archive.archiver import archiver
from bes.archive.archive_util import archive_util

class archive_cli_command(object):
  
  @classmethod
  def create_git(clazz, root_dir, prefix, revision, output_filename, archive_format):
    r = git_repo(root_dir)
    r.archive_foo(prefix, revision, output_filename,
                  archive_format = archive_format,
                  short_hash = True)
    return 0

  @classmethod
  def remove_members(clazz, archive, members):
    archive_util.remove_members(archive, members)
    return 0

  @classmethod
  def contents(clazz, archive):
    for member in archiver.members(archive):
      print(member)
    return 0
  
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
  def combine(clazz, dest_archive, archives, check_content, base_dir, exclude):
    archive_util.combine(archives, dest_archive,
                         check_content = check_content,
                         base_dir = base_dir,
                         exclude = exclude)
    return 0

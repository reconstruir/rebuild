#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.fs import tar_util, temp_file
from bes.system import execute
from bes.git import git
from rebuild.base import build_target, package_descriptor
from rebuild.manager import rebuild_manager
from rebuild.package import artifact_manager
from rebuild.package.unit_test_packages import unit_test_packages

class test_rebuild_manager(unittest.TestCase):

  DEBUG = False
  #DEBUG = True

  # FIXME: this code is cut-n-pasted from artifact_manager.py
  def __make_test_artifacts_git_repo(self):
    tmp_repo = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print("tmp_repo:\n%s\n" % (tmp_repo))
    unit_test_packages.make_test_packages(unit_test_packages.TEST_PACKAGES, tmp_repo)
    assert not git.is_repo(tmp_repo)
    git.init(tmp_repo)
    git.add(tmp_repo, '.')
    git.commit(tmp_repo, 'unittest', '.')
    return self.__make_test_artifact_manager(address = tmp_repo)

  @classmethod
  def __make_test_artifact_manager(clazz, address = None, items = None):
    publish_dir = temp_file.make_temp_dir(delete = not clazz.DEBUG)
    if clazz.DEBUG:
      print("publish_dir:\n%s\n" % (publish_dir))
    am = artifact_manager(publish_dir, address = address)
    if items:
      unit_test_packages.make_test_packages(items, am.publish_dir)
    return am

  def xxxtest_update_tools(self):
    am = self.__make_test_artifacts_git_repo()
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    rebbe = rebuild_manager(root_dir = tmp_dir, artifact_manager = am)
    if self.DEBUG:
      print("tmp_dir:\n%s\n" % (tmp_dir))

    packages = [
      package_descriptor.parse('water-1.0.0-0'),
      package_descriptor.parse('mercury-1.2.8-0'),
      package_descriptor.parse('arsenic-1.2.9-0'),
    ]

    rebbe.update_tools(packages)

    for package_info in packages:
      tool_name = package_info.name + '_script.sh'
      exe = rebbe.tool_exe(package_info, tool_name)
      rv = execute.execute(exe)
      self.assertEqual( 0, rv.exit_code )
      self.assertEqual( package_info.full_name, rv.stdout.strip() )

if __name__ == '__main__':
  unittest.main()

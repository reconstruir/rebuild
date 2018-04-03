#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple
from bes.fs import file_checksum, file_util, temp_file
from bes.archive import archiver
from .lipo import lipo

class fat_archive(object):

  AnalyzeResult = namedtuple('AnalyzeResult', [ 'objects', 'normals' ])

  class MemberInfo(object):
    def __init__(self, member, dest_dir):
      self.member = member
      self.filename = path.join(dest_dir, member)
      self.checksum = file_checksum.file_checksum(self.filename)

    def __str__(self):
      return str(self.member)
      
  class ThinPackage(object):
    def __init__(self, filename, extract_dir, members):
      self.filename = filename
      self.extract_dir = extract_dir
      self.members = members

    def dump(self, indent = 0):
      spaces = ''.zfill(indent).replace('0', ' ')
      print("%sthin_package: %s" % (spaces, self.filename))
      print("%s extract_dir: %s" % (spaces, self.extract_dir))
      print("%s     objects: %s" % (spaces, [ str(x) for x in self.members.objects ]))
      print("%s     normals: %s" % (spaces, [ str(x) for x in self.members.normals ]))

    def normals_checksums(self):
      return [ m.checksum for m in self.members.normals ]
      
    def compare_normals(self, others):
      mine_checksums = self.normals_checksums()
      for other in others:
        other_checksums = other.normals_checksums()
        if mine_checksums != other_checksums:
          return False, other
      return True, None

  @classmethod
  def thin_to_fat(clazz, thin_packages_filenames, fat_package_filename, lipo_exe = None):
    tmp_extract_dir = temp_file.make_temp_dir()
    thin_packages = clazz.__load_thin_packages(thin_packages_filenames, tmp_extract_dir, lipo_exe = lipo_exe)

    # Check that the non object files in all thin packages are the same
    for thin_package in thin_packages:
      others = [ p for p in thin_packages if p != thin_package ]
      success, failed_package = thin_package.compare_normals(others)
      if not success:
        raise RuntimeError('The content of non object files in %s and %s does not match.' % (thin_package.filename, failed_package.filename))

    # Collect the objects into a dictionary keyed by the arcname in the final fat package
    files = {}
    for thin_package in thin_packages:
      for obj in thin_package.members.objects:
        if obj.member not in files:
          files[obj.member] = []
        files[obj.member].append(obj)

    tmp_repack_dir = temp_file.make_temp_dir()
        
    for arcname, thin_objects in files.items():
      fat_object_filename = path.join(tmp_repack_dir, arcname)
      thin_objects_filenames = [ obj.filename for obj in thin_objects ]
      file_util.mkdir(path.dirname(fat_object_filename))
      lipo.thin_to_fat(thin_objects_filenames, fat_object_filename, lipo_exe = lipo_exe)

    # Extract the normal non object files
    for thin_package in thin_packages:
      members = [ member_info.member for member_info in thin_package.members.normals ]
      archiver.extract_members(thin_package.filename, members, tmp_repack_dir)

    # Re-pack the final fat archive
    archiver.create(fat_package_filename, tmp_repack_dir)
      
  @classmethod
  def __load_thin_packages(clazz, thin_packages_filenames, dest_dir, lipo_exe = None):
    thin_packages = []
    for i, thin_package_filename in enumerate(thin_packages_filenames):
      extract_dir = path.join(dest_dir, str(i))
      members = clazz.__extract_and_analyze(thin_package_filename, extract_dir, lipo_exe = lipo_exe)
      thin_package = clazz.ThinPackage(thin_package_filename, extract_dir, members)
      thin_packages.append(thin_package)
    return thin_packages
      
  @classmethod
  def __extract_and_analyze(clazz, thin_package, dest_dir, lipo_exe = None):
    archiver.extract(thin_package, dest_dir)
    members = archiver.members(thin_package)
    members_infos = [ clazz.MemberInfo(member, dest_dir) for member in members ]
    object_members = [ info for info in members_infos if lipo.is_valid_object(info.filename) ]
    normal_members = [ info for info in members_infos if info not in object_members ]
    return clazz.AnalyzeResult(object_members, normal_members)

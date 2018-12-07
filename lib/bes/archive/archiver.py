#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_cache
from bes.system import host
from .archive_tar import archive_tar
from .archive_zip import archive_zip
from .archive_dmg import archive_dmg
from .archive_xz import archive_xz
from .archive_extension import archive_extension
from .archive_base import archive_base

class archiver(object):
  'Class to deal with archives.'

  item = archive_base.item
  
  @classmethod
  def is_valid(clazz, filename):
    if not path.exists(filename):
      return False
    if not path.isfile(filename):
      return False
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      return False
    return archive_class.file_is_valid(filename)
  
  @classmethod
  def members(clazz, filename):
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).members

  @classmethod
  def has_member(clazz, filename, member):
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).has_member(member)

  @classmethod
  def extract_all(clazz, filename, dest_dir, base_dir = None,
                  strip_common_ancestor = False, strip_head = None):
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    archive = archive_class(filename)
    return archive.extract_all(dest_dir,
                               base_dir = base_dir,
                               strip_common_ancestor = strip_common_ancestor,
                               strip_head = strip_head)

  @classmethod
  def extract(clazz, filename, dest_dir, base_dir = None,
              strip_common_ancestor = False, strip_head = None,
              include = None, exclude = None):
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    archive = archive_class(filename)
    return archive.extract(dest_dir,
                           base_dir = base_dir,
                           strip_common_ancestor = strip_common_ancestor,
                           strip_head = strip_head,
                           include = include,
                           exclude = exclude)

  @classmethod
  def extract_member_to_string(clazz, archive, member):
    archive_class = clazz._determine_type(archive)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (archive))
    return archive_class(archive).extract_member_to_string(member)

  @classmethod
  def extract_member_to_string_cached(clazz, archive, member, root_dir = None):
    from .archive_member_cache_item import archive_member_cache_item
    item = archive_member_cache_item(archive, member)
    return file_cache.cached_item(item, root_dir)
  
  @classmethod
  def extract_member_to_file(clazz, archive, member, filename):
    archive_class = clazz._determine_type(archive)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (archive))
    return archive_class(archive).extract_member_to_file(member, filename)

  @classmethod
  def create(clazz, filename, root_dir, base_dir = None,
             extra_items = None,
             include = None, exclude = None):
    archive_class = clazz._determine_type_for_create(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).create(root_dir,
                                          base_dir = base_dir,
                                          extra_items = extra_items,
                                          include = include,
                                          exclude = exclude)

  @classmethod
  def common_base(clazz, filename):
    archive_class = clazz._determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).common_base()

  @classmethod
  def _determine_type(clazz, filename):
    possible = [ archive_tar, archive_zip, archive_xz ] 
    if host.SYSTEM == host.MACOS:
      possible.append(archive_dmg)

    for p in possible:
      if p.file_is_valid(filename):
        return p
    return None

  @classmethod
  def _determine_type_for_create(clazz, filename):
    if archive_extension.is_valid_tar_filename(filename):
      return archive_tar
    elif archive_extension.is_valid_zip_filename(filename):
      return archive_zip
    elif archive_extension.is_valid_xz_filename(filename):
      return archive_xz
    elif archive_extension.is_valid_dmg_filename(filename):
      return archive_dmg
    return None

  @classmethod
  def common_files(clazz, archives):
    'Return a list of files common to 2 or more archives.' 
    sets = [ set(clazz.members(a)) for a in archives ]
    return list(set.intersection(*sets))

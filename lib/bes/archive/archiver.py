#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path
from bes.fs import file_cache
from .archive_tar import archive_tar
from .archive_zip import archive_zip
from .archive_extension import archive_extension

class archiver(object):
  'Class to deal with archives.'

  @classmethod
  def is_valid(clazz, filename):
    if not path.exists(filename):
      return False
    if not path.isfile(filename):
      raise False
    archive_class = clazz.__determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).is_valid()
  
  @classmethod
  def members(clazz, filename):
    archive_class = clazz.__determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).members()

  @classmethod
  def extract(clazz, filename, dest_dir, base_dir = None,
              strip_common_base = False, strip_head = None,
              include = None, exclude = None):
    archive_class = clazz.__determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).extract(dest_dir,
                                           base_dir = base_dir,
                                           strip_common_base = strip_common_base,
                                           strip_head = strip_head,
                                           include = include,
                                           exclude = exclude)

  @classmethod
  def extract_members(clazz, filename, members, dest_dir, base_dir = None,
                      strip_common_base = False, strip_head = None,
                      include = None, exclude = None):
    archive_class = clazz.__determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).extract_members(members,
                                                  dest_dir,
                                                  base_dir = base_dir,
                                                  strip_common_base = strip_common_base,
                                                  strip_head = strip_head,
                                                  include = include,
                                                  exclude = exclude)

  @classmethod
  def extract_member_to_string(clazz, archive, member):
    archive_class = clazz.__determine_type(archive)
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
    archive_class = clazz.__determine_type(archive)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (archive))
    return archive_class(archive).extract_member_to_file(member, filename)

  @classmethod
  def create(clazz, filename, root_dir, base_dir = None,
             extra_items = None,
             include = None, exclude = None):
    archive_class = clazz.__determine_type_for_create(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).create(root_dir,
                                          base_dir = base_dir,
                                          extra_items = extra_items,
                                          include = include,
                                          exclude = exclude)

  @classmethod
  def common_base(clazz, filename):
    archive_class = clazz.__determine_type(filename)
    if not archive_class:
      raise RuntimeError('Unknown archive type for %s' % (filename))
    return archive_class(filename).common_base()

  @classmethod
  def __determine_type(clazz, filename):
    if archive_tar(filename).is_valid():
      return archive_tar
    elif archive_zip(filename).is_valid():
      return archive_zip
    return None

  @classmethod
  def __determine_type_for_create(clazz, filename):
    if archive_extension.is_valid_tar_filename(filename):
      return archive_tar
    elif archive_extension.is_valid_zip_filename(filename):
      return archive_zip
    return None
  

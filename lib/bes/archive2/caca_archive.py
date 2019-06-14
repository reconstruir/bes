#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from collections import namedtuple

from bes.common import algorithm
from bes.property.cached_property import cached_property
from bes.fs.file_find import file_find
from bes.fs.file_path import file_path
from bes.fs.file_util import file_util
from bes.fs.file_copy import file_copy
from bes.fs.temp_file import temp_file
from bes.match.matcher_always_false import matcher_always_false
from bes.match.matcher_always_true import matcher_always_true
from bes.match.matcher_multiple_filename import matcher_multiple_filename
from bes.match.matcher_util import matcher_util

from .archive_base import archive_base

class archive(archive_base):
  '''
  An archive class that implements common things for archives but keeps the abstract parts
  of archive_base so concrete subclasses are still needed for different formats.
  '''
  
  def __init__(self, filename):
    self._filename = filename

  @property
  def filename(self):
    return self._filename

  @filename.setter
  def filename(self, filename):
    raise AttributeError('filename is read-only.')
  
  @cached_property
  def members(self):
    '''
    Return cached members.  Note that unless the underlying filename is intentionally
    hacked, the cached members are valid forever.
    '''
    return self._normalize_members(self._get_members())

  @cached_property
  def file_members(self):
    '''Return members that are files only.'''
    return [ f for f in self.members if self.content_is_file(f) ]

  @cached_property
  def dir_members(self):
    '''Return members that are dirs only.'''
    return [ f for f in self.members if self.content_is_dir(f) ]

  @classmethod
  def content_is_file(clazz, filename):
    '''Return True if filename is a file.'''
    return not filename.endswith('/')
      
  @classmethod
  def content_is_dir(clazz, filename):
    '''Return True if filename is a dir.'''
    return filename.endswith('/')

  @abstractmethod
  def create(self, root_dir, base_dir = None,
             extra_items = None,
             include = None, exclude = None):
    raise NotImplementedError()

  def extract_member_to_file(self, member, filename):
    tmp_dir = temp_file.make_temp_dir()
    tmp_member = path.join(tmp_dir, member)
    self.extract(tmp_dir, include = [ member ])
    if not path.exists(tmp_member):
      raise RuntimeError('Failed to extract member: %s' % (member))
    if not path.isfile(tmp_member):
      raise RuntimeError('Member is not a file: %s' % (member))
    file_util.rename(tmp_member, filename)

  def extract_member_to_string(self, member):
    tmp_file = temp_file.make_temp_file()
    self.extract_member_to_file(member, tmp_file)
    result = file_util.read(tmp_file)
    file_util.remove(tmp_file)
    return result

  def common_ancestor(self):
    'Return a common ancestor dir for the archive or None if no common base exists.'
    return self._common_ancestor_for_members(self.members)

  @classmethod
  def _normalize_members(clazz, members):
    'Normalize the archive members to be unique and sorted.'
    return sorted(algorithm.unique(members))

  # Some archives have some dumb members that are immaterial to common base
  COMMON_BASE_MEMBERS_EXCLUDE = [ '.' ]

  @classmethod
  def _common_ancestor_for_members(clazz, members):
    'Return a common base dir for the given members or None if no common base exists.'
    members = [ m for m in members if m not in clazz.COMMON_BASE_MEMBERS_EXCLUDE ]
    return file_path.common_ancestor(members)

  @classmethod
  def _find(clazz, root_dir, base_dir, extra_items, include, exclude):
    files = file_find.find(root_dir, relative = True, file_type = file_find.FILE | file_find.LINK)
    items = []

    if include:
      include_matcher = matcher_multiple_filename(include)
    else:
      include_matcher = matcher_always_true()

    if exclude:
      exclude_matcher = matcher_multiple_filename(exclude)
    else:
      exclude_matcher = matcher_always_false()

    for f in files:
      filename = path.join(root_dir, f)
      if base_dir:
        arcname = path.join(base_dir, f)
      else:
        arcname = f

      should_include = include_matcher.match(f)
      should_exclude = exclude_matcher.match(f)

      if should_include and not should_exclude:
        items.append(clazz.Item(filename, arcname))

    return items + (extra_items or [])

  @classmethod
  def _determine_dest_dir(clazz, dest_dir, base_dir):
    if base_dir:
      dest_dir = path.join(dest_dir, base_dir)
    else:
      dest_dir = dest_dir
    file_util.mkdir(dest_dir)
    return dest_dir

  def _handle_extract_strip_common_ancestor(self, members, strip_common_ancestor, strip_head, dest_dir):
    if strip_common_ancestor:
      common_ancestor = self._common_ancestor_for_members(members)
      if common_ancestor:
        from_dir = path.join(dest_dir, common_ancestor)
        file_copy.copy_tree(from_dir, dest_dir)
        file_util.remove(from_dir)
    if strip_head:
      from_dir = path.join(dest_dir, strip_head)
      if path.isdir(from_dir):
        file_copy.copy_tree(from_dir, dest_dir)
        file_util.remove(from_dir)
      
  def _pre_create(self):
    'Setup some stuff before create() is called.'
    d = path.dirname(self.filename)
    if d:
      file_util.mkdir(d)

  @classmethod
  def _filter_for_extract(clazz, members, include, exclude):
    return matcher_util.match_filenames(members, include, exclude)

  @classmethod
  def _handle_post_extract(clazz, dest_dir, include, exclude):
    files = self._find(dest_dir, None, None, include, exclude)
    for f in files:
      print('include: %s' % (f))

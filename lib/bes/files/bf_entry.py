#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import stat

from os import path
from collections import namedtuple

from bes.common.hash_util import hash_util
from bes.common.time_util import time_util
from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger
from bes.system.filesystem import filesystem

from .bf_date import bf_date
from .bf_date_comparison_type import bf_date_comparison_type
from .bf_entry_sort_criteria import bf_entry_sort_criteria
from .bf_error import bf_error
from .bf_file_type import bf_file_type
from .bf_filename import bf_filename
from .bf_mtime_cached_info import bf_mtime_cached_info
from .bf_path_type import bf_path_type
from .bf_path import bf_path
from .bf_permission_error import bf_permission_error
from .bf_symlink import bf_symlink

from .attr.bf_attr_file import bf_attr_file
from .metadata.bf_metadata_file import bf_metadata_file

class bf_entry(object):

  _log = logger('bf_entry')
  
  def __init__(self, filename, root_dir = None):
    check.check_string(filename)
    check.check_string(root_dir, allow_none = True)

    filename = path.normpath(filename)
    root_dir = path.normpath(root_dir) if root_dir else None

    if root_dir:
      if path.isabs(filename):
        raise bf_error(f'if root_dir is given then filename cannot be absolute: "{filename}"')
      if not path.isabs(root_dir):
        raise bf_error(f'root_dir has to be absolute: "{root_dir}"')
    
    self._filename = filename
    self._root_dir = root_dir

  @cached_property
  def filename(self):
    if self._root_dir:
      return path.join(self._root_dir, self._filename)
    return self._filename

  @property
  def root_dir(self):
    return self._root_dir

  @cached_property
  def absolute_filename(self):
    if self._root_dir:
      return path.join(self._root_dir, self._filename)
    if path.isabs(self._filename):
      return self._filename
    return path.abspath(self._filename)

  @cached_property
  def absolute_filename_lowercase(self):
    absolute_filename = self.relative_filename
    if absolute_filename == None:
      return None
    return absolute_filename.lower()
  
  @cached_property
  def relative_filename(self):
    if not self._root_dir:
      return self._filename
    if path.isabs(self._filename):
      return bf_filename.remove_head(self._filename, self._root_dir)
    return self._filename

  @cached_property
  def relative_filename_lowercase(self):
    relative_filename = self.relative_filename
    if relative_filename == None:
      return None
    return relative_filename.lower()

  @cached_property
  def is_absolute(self):
    return path.isabs(self.filename)

  @cached_property
  def is_relative(self):
    return not path.isabs(self.filename)
  
  def __str__(self):
    return self.filename

  def __repr__(self):
    return self.filename
  
  def __eq__(self, other):
    if other == None:
      return False
    elif check.is_bf_entry(other):
      return self.filename == other.filename
    elif check.is_string(other):
      return self.filename == other
    else:
      raise ValueError(f'Trying to compare against unknown type: "{other}" - {type(other)}')

  def __lt__(self, other):
    if other == None:
      return -1
    elif check.is_bf_entry(other):
      return self.filename < other.filename
    elif check.is_string(other):
      return self.filename < other
    else:
      raise ValueError(f'Trying to compare against unknown type: "{other}" - {type(other)}')
    
  @cached_property
  def filename_lowercase(self):
    return self.filename.lower()
  
  @cached_property
  def dirname(self):
    return path.dirname(self.filename)

  @cached_property
  def dirname_lowercase(self):
    return self.dirname.lower()
  
  @cached_property
  def basename(self):
    return path.basename(self.filename)

  @cached_property
  def extension(self):
    return bf_filename.extension(self.filename)

  @cached_property
  def extension_lowercase(self):
    return self.extension.lower()
  
  @property
  def exists(self):
    return path.exists(self.filename)

  @property
  def is_readable(self):
    return os.access(self.filename, os.R_OK)

  @property
  def is_writable(self):
    return os.access(self.filename, os.W_OK)

  @property
  def is_executable(self):
    return os.access(self.filename, os.F_OK)
  
  _access_result = namedtuple('_access_result', 'exists, can_read, can_write, can_execute')
  @property
  def access(self):
    exists = os.access(self.filename, os.F_OK)
    if exists:
      can_read = os.access(self.filename, os.R_OK)
      can_write = os.access(self.filename, os.W_OK)
      can_execute = os.access(self.filename, os.X_OK)
    else:
      can_read = False
      can_write = False
      can_execute = False
    return self._access_result(exists, can_read, can_write, can_execute)
  
  @property
  def stat(self):
    return os.stat(self.filename)

  @property
  def lstat(self):
    return os.lstat(self.filename)
  
  @property
  def is_link(self):
    return stat.S_ISLNK(self.lstat.st_mode)

  @property
  def is_broken_link(self):
    return bf_symlink.is_broken(self.filename)

  @cached_property
  def _cached_resolved_link(self):
    return bf_mtime_cached_info(self.filename, lambda f_: bf_symlink.resolve(f_))
  
  @property
  def resolved_link(self):
    return self._cached_resolved_link.value
  
  @cached_property
  def hashed_filename_sha256(self):
    return hash_util.hash_string_sha256(self.filename)
  
  @cached_property
  def basename_lowercase(self):
    return self.basename.lower()

  @property
  def is_dir(self):
    return stat.S_ISDIR(self.stat.st_mode)
  
  @property
  def is_file(self):
    return stat.S_ISREG(self.stat.st_mode)

  @property
  def is_block_device(self):
    return stat.S_ISBLK(self.stat.st_mode)

  @property
  def is_char_device(self):
    return stat.S_ISCHR(self.stat.st_mode)
  
  @property
  def is_device(self):
    return self.is_block_device or self.is_char_device

  @property
  def file_type(self):
    if self.is_link:
      return bf_file_type.LINK
    elif self.is_file:
      return bf_file_type.FILE
    elif self.is_dir:
      return bf_file_type.DIR
    elif self.is_device:
      return bf_file_type.DEVICE
    raise bf_error(f'unexpected file type: "{self.filename}"')

  def file_type_matches(self, mask):
    mask = check.check_bf_file_type(mask)

    return (self.file_type & mask) != 0
  
  @property
  def size(self):
    return self.stat.st_size

  @property
  def is_empty(self):
    return self.size == 0

  @property
  def device_id(self):
    return self.stat.st_dev

  @property
  def inode_number(self):
    return self.stat.st_ino

  @property
  def mtime(self):
    return self.stat.st_mtime

  @property
  def mode(self):
    'Return only the lower bits of a inode mode (permissions)'
    return self.stat.st_mode & 0o777
  
  @property
  def modification_date(self):
    return bf_date.get_modification_date(self.filename)

  @modification_date.setter
  def modification_date(self, mtime):
    check.check_datetime(mtime)

    bf_date.set_modification_date(self.filename, mtime)

  @property
  def modification_date_timestamp(self):
    return time_util.timestamp(when = self.modification_date, milliseconds = False)

  def compare_modification_date(self, other_date):
    check.check_datetime(other_date)

    date = self.modification_date
    if date < other_date:
      return -1
    elif date > other_date:
      return 1
    else:
      pass
    assert date == other_date
    return 0

  def modification_date_matches(self, date, comparison_type):
    check.check_datetime(date)
    comparison_type = check.check_bf_date_comparison_type(comparison_type)

    cmp_rv = self.compare_modification_date(date)
    if comparison_type == bf_date_comparison_type.EQ:
      return cmp_rv == 0
    elif comparison_type == bf_date_comparison_type.GE:
      return cmp_rv in ( 0, 1 )
    elif comparison_type == bf_date_comparison_type.GT:
      return cmp_rv == 1
    elif comparison_type == bf_date_comparison_type.LE:
      return cmp_rv in ( 0, -1 )
    elif comparison_type == bf_date_comparison_type.LT:
      return cmp_rv == -1
    elif comparison_type == bf_date_comparison_type.NE:
      return cmp_rv != 0
    else:
      assert False, f'Not reached'

  # FIXME: this is kinda wrong
  def modification_date_matches_delta(self, delta, comparison_type):
    check.check_timedelta(delta)
    comparison_type = check.check_bf_date_comparison_type(comparison_type)

    date = self.modification_date + delta
    return self.modification_date_matches(date, comparison_type)
      
  def touch(self):
    bf_date.touch(self.filename)
  
  @property
  def is_hidden(self):
   return filesystem.file_is_hidden(self.filename)
  
  @cached_property
  def attributes(self):
    return bf_attr_file(self.filename)

  @cached_property
  def metadata(self):
    from .metadata_factories.bf_metadata_factory_checksum import bf_metadata_factory_checksum
    from .metadata_factories.bf_metadata_factory_mime import bf_metadata_factory_mime
    return bf_metadata_file(self.filename)

  @property
  def media_type(self):
    return self.metadata['bes/mime/media_type/1.0']

  @property
  def mime_type(self):
    return self.metadata['bes/mime/mime_type/1.0']

  @property
  def checksum_md5(self):
    return self.metadata['bes/checksum/md5/0.0']
  
  @property
  def checksum_sha1(self):
    return self.metadata['bes/checksum/sha1/0.0']

  @property
  def checksum_sha256(self):
    return self.metadata['bes/checksum/sha256/0.0']

  @property
  def has_checksum_md5(self):
    return 'bes/checksum/md5/0.0' in self.metadata

  @property
  def has_checksum_sha1(self):
    return 'bes/checksum/sha1/0.0' in self.metadata
  
  @property
  def has_checksum_sha256(self):
    return 'bes/checksum/sha256/0.0' in self.metadata
  
  @property
  def is_media(self):
    return self.is_file and self.media_type in ( 'image', 'video' )

  @property
  def is_image(self):
    return self.is_file and self.media_type in ( 'image' )

  @property
  def is_video(self):
    return self.is_file and self.media_type in ( 'video' )

  @classmethod
  def _cast_func(clazz, o):
    if check.is_bf_entry(o):
      return 0
    elif check.is_string(o):
      return bf_entry(o)
    else:
      raise TypeError(f'unknown cast type for bf_entry: "{o}" - {type(o)}')

  def filename_for_matcher(self, path_type, ignore_case):
    path_type = check.check_bf_path_type(path_type, allow_none = True)
    check.check_bool(ignore_case)

    path_type = path_type or bf_path_type.BASENAME
    filename = None
    if path_type == bf_path_type.ABSOLUTE:
      filename = self.absolute_filename_lowercase if ignore_case else self.absolute_filename
    elif path_type == bf_path_type.BASENAME:
      filename = self.basename_lowercase if ignore_case else self.basename
    elif path_type == bf_path_type.RELATIVE:
      filename = self.relative_filename_lowercase if ignore_case else self.relative_filename
    else:
      assert False, f'unknown path_type: "{path_type}"'
    assert filename != None
    return filename

  def content_is_same(self, other, read_size = 1024 * 1024):
    check.check_bf_entry(other)
    check.check_int(read_size)
    
    if self.size != other.size:
      return False

    with open(self.filename, 'rb') as f1:
      with open(other.filename, 'rb') as f2:
        if f1.read(read_size) != f2.read(read_size):
          return False
    return True

  def compare(self, other, sort_criteria):
    check.check_bf_entry(other)
    sort_criteria = check.check_bf_entry_sort_criteria(sort_criteria)

    self_criteria = self._compare_criteria(sort_criteria)
    other_criteria = other._compare_criteria(sort_criteria)
    return cmp(self_criteria, other_criteria)

  def _compare_criteria(self, sort_criteria):
    sort_criteria = check.check_bf_entry_sort_criteria(sort_criteria)

    if sort_criteria == bf_entry_sort_criteria.BASENAME:
      return ( self.basename, )
    elif sort_criteria == bf_entry_sort_criteria.BASENAME_LOWERCASE:
      return ( self.basename_lowercase, )
    elif sort_criteria == bf_entry_sort_criteria.DIRNAME:
      return ( self.dirname, self.basename )
    elif sort_criteria == bf_entry_sort_criteria.DIRNAME_LOWERCASE:
      return ( self.dirname_lowercase, self.basename_lowercase )
    elif sort_criteria == bf_entry_sort_criteria.FILENAME:
      return ( self.filename, )
    elif sort_criteria == bf_entry_sort_criteria.FILENAME_LOWERCASE:
      return ( self.filename_lowercase, )
    elif sort_criteria == bf_entry_sort_criteria.MODIFICATION_DATE:
      return ( self.modification_date, self.filename_lowercase )
    elif sort_criteria == bf_entry_sort_criteria.SIZE:
      return ( self.size, self.filename_lowercase )
    else:
      assert False

  def clone_replace_root_dir(self, root_dir):
    check.check_string(root_dir)

    return bf_entry(self._filename, root_dir = root_dir)

  def read_content(self):
    with open(self.filename, 'rb') as f:
      return f.read()

  @cached_property
  def decomposed_path(self):
    return bf_path.decompose(self.absolute_filename)
    
check.register_class(bf_entry, include_seq = False, cast_func = bf_entry._cast_func)

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
from collections import namedtuple

from bes.common.hash_util import hash_util
from bes.common.time_util import time_util
from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from .bfile_date import bfile_date
from .bfile_error import bfile_error
from .bfile_filename import bfile_filename
from .bfile_mtime_cached_info import bfile_mtime_cached_info
from .bfile_permission_error import bfile_permission_error

from .attr.bfile_attr_file import bfile_attr_file
from .metadata.bfile_metadata_file import bfile_metadata_file

class bfile_entry(object):

  _log = logger('bfile_entry')
  
  def __init__(self, filename):
    self._filename = filename
    self._stat = bfile_mtime_cached_info(self._filename, lambda f: os.stat(filename, follow_symlinks = True))

  @property
  def filename(self):
    return self._filename

  @cached_property
  def filename_lowercase(self):
    return self.filename.lower()
  
  @cached_property
  def dirname(self):
    return path.dirname(self._filename)

  @cached_property
  def dirname_lowercase(self):
    return self.dirname.lower()
  
  @cached_property
  def basename(self):
    return path.basename(self._filename)

  @cached_property
  def extension(self):
    return bfile_filename.extension(self._filename)

  @cached_property
  def extension_lowercase(self):
    return self.extension.lower()
  
  @property
  def exists(self):
    return  path.exists(self._filename)

  @property
  def is_readable(self):
    return os.access(self._filename, os.R_OK)

  @property
  def is_writable(self):
    return os.access(self._filename, os.W_OK)

  @property
  def is_executable(self):
    return os.access(self._filename, os.F_OK)
  
  _access_result = namedtuple('_access_result', 'exists, can_read, can_write, can_execute')
  @property
  def access(self):
    exists = os.access(self._filename, os.F_OK)
    if exists:
      can_read = os.access(self._filename, os.R_OK)
      can_write = os.access(self._filename, os.W_OK)
      can_execute = os.access(self._filename, os.X_OK)
    else:
      can_read = False
      can_write = False
      can_execute = False
    return self._access_result(exists, can_read, can_write, can_execute)
  
  @property
  def stat(self):
    return self._stat.value

  @cached_property
  def hashed_filename_sha256(self):
    return hash_util.hash_string_sha256(self._filename)
  
  @cached_property
  def basename_lowercase(self):
    return self.basename.lower()

  @property
  def is_dir(self):
    return path.isdir(self._filename)
  
  @property
  def is_file(self):
    return path.isfile(self._filename)
  
  @property
  def size(self):
    return self.stat.st_size
  
  @property
  def modification_date(self):
    return bfile_date.get_modification_date(self._filename)

  @modification_date.setter
  def modification_date(self, mtime):
    check.check_datetime(mtime)

    bfile_date.set_modification_date(self._filename, mtime)

  @property
  def modification_date_timestamp(self):
    return time_util.timestamp(when = self.modification_date, milliseconds = False)

  @cached_property
  def attributes(self):
    return bfile_attr_file(self._filename)

  @cached_property
  def metadata(self):
    from .metadata_factories.bfile_metadata_factory_checksum import bfile_metadata_factory_checksum
    from .metadata_factories.bfile_metadata_factory_mime import bfile_metadata_factory_mime
    return bfile_metadata_file(self._filename)

  @property
  def media_type(self):
    return self.metadata['bes/mime/media_type/1.0']

  @property
  def mime_type(self):
    return self.metadata['bes/mime/mime_type/1.0']

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
  
check.register_class(bfile_entry, include_seq = False)

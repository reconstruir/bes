#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
from datetime import datetime

from ..system.check import check
from ..property.cached_property import cached_property
from ..fs.file_attributes_metadata import file_attributes_metadata
from ..fs.file_check import file_check
from ..compat.cmp import cmp

class file_entry(object):

  def __init__(self, filename):
    self._filename = file_check.check_file(filename)

  @property
  def exists(self):
    return path.exists(self._filename)
    
  @cached_property
  def stat(self):
    return os.stat(self._filename, follow_symlinks = True)
    
  @cached_property
  def basename(self):
    return path.basename(self._filename)
  
  @cached_property
  def basename_lowercase(self):
    return self.basename.lower()

  @cached_property
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
  def is_dir(self):
    return path.isdir(self._filename)
  
  @cached_property
  def is_file(self):
    return path.isfile(self._filename)
  
  @cached_property
  def size(self):
    return self.stat.st_size
  
  @property
  def date(self):
    ts = path.getmtime(self._filename)
    return datetime.fromtimestamp(ts)

  @date.setter
  def date(self, mtime):
    check.check(mtime, datetime)

    ts = mtime.timestamp()
    os.utime(self._filename, ( ts, ts ))
  
  @property
  def media_type(self):
    return file_attributes_metadata.get_media_type(self._filename,
                                                   fallback = True,
                                                   cached = True)

  @property
  def mime_type(self):
    return file_attributes_metadata.get_mime_type(self._filename,
                                                  fallback = True,
                                                  cached = True)

  @property
  def is_media(self):
    return self.is_file and self.media_type in ( 'image', 'video' )

  @property
  def is_image(self):
    return self.is_file and self.media_type in ( 'image' )

  @property
  def is_video(self):
    return self.is_file and self.media_type in ( 'video' )

check.register_class(file_entry, include_seq = False)

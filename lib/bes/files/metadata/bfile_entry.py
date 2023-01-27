#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
import time
import os
from os import path
from datetime import datetime

from bes.system.check import check
from bes.property.cached_property import cached_property
#from ..fs.file_attributes_metadata import file_attributes_metadata
from bes.fs.file_check import file_check

from .bfile_cached_attributes import bfile_cached_attributes

class bfile_entry(object):

  def __init__(self, filename):
    self._filename = file_check.check_file(filename)
    self._cached_attributes = bfile_cached_attributes(self._filename)

  @property
  def exists(self):
    return path.exists(self._filename)
    
  @property
  def stat(self):
    return self._cached_attributes.get_value('stat')
    
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
    ts = path.getmtime(self._filename)
    return datetime.fromtimestamp(ts)

  @date.setter
  def modification_date(self, mtime):
    check.check_datetime(datetime)

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

'''
#file_entry.register_metadata_getter('cv', 'faces', '1.0.0', clazz)

fi = file_entry('/foo/caca.jpg')
fi.tags.is_favorite = True
fi.tags.checksum_sha256

fi.get_metadata('checksum', 'sha256', '1.0.0')
'''
  
check.register_class(bfile_entry, include_seq = False)

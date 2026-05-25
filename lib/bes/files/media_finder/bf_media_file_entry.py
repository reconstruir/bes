#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import dataclasses
import os.path as path

from bes.system.check import check

@dataclasses.dataclass(frozen=True)
class bf_media_file_entry:
  root_dir:   str   # which scan root this file was found under
  filename:   str   # absolute path (matches bf_entry.filename convention)
  size:       int
  mtime:      float
  extension:  str
  mime_type:  str
  media_type: str   # 'image' | 'video' | 'other'

  @property
  def relative_filename(self):
    return path.relpath(self.filename, self.root_dir)

  def __str__(self):
    return self.filename

check.register_class(bf_media_file_entry, include_seq=False)

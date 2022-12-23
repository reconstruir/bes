#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from bes.system.check import check
from bes.system.log import logger

from .file_resolver import file_resolver

class file_resolver_mixin:

  def easy_resolve_media_files(self, files, **kargs):
    check.check_string_seq(files)

    if 'media_types' in kargs:
      media_types = kargs['media_types']
      kargs = copy.deepcopy(kargs)
      del kargs['media_types']
    else:
      media_types = self.options.media_types or ( 'image', 'video' )
    
    return file_resolver.easy_resolve_media_files(files,
                                                  self.options.recursive,
                                                  self.options.file_ignorer,
                                                  media_types,
                                                  **kargs)

  def easy_resolve_image_files(self, files, **kargs):
    check.check_string_seq(files)

    return file_resolver.easy_resolve_media_files(files,
                                                  self.options.recursive,
                                                  self.options.file_ignorer,
                                                  ( 'image', ),
                                                  **kargs)

  def easy_resolve_video_files(self, files, **kargs):
    check.check_string_seq(files)

    return file_resolver.easy_resolve_media_files(files,
                                                  self.options.recursive,
                                                  self.options.file_ignorer,
                                                  ( 'video', ),
                                                  **kargs)

  def easy_resolve_document_files(self, files, **kargs):
    check.check_string_seq(files)

    return file_resolver.easy_resolve_media_files(files,
                                                  self.options.recursive,
                                                  self.options.file_ignorer,
                                                  ( 'document', ),
                                                  **kargs)
  

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_util import file_util
from ..system.check import check
from bes.common.object_util import object_util

from .archive_operation_base import archive_operation_base

class archive_operation_remove_files(archive_operation_base):
  'Remove files from an archive.'

  def __init__(self, file_arcnames):
    self._file_arcnames = object_util.listify(file_arcnames)
               
  #@abstractmethod
  def execute(self, temp_dir):
    'Execute this operation in a temp_dir of the unpacked archive.'
    filenames = [ path.join(temp_dir, arcname) for arcname in self._file_arcnames ]
    file_util.remove(filenames)

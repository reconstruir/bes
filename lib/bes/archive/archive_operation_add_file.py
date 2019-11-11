#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_util import file_util
from bes.common.check import check

from .archive_operation_base import archive_operation_base

class archive_operation_add_file(archive_operation_base):
  'Add a file to an archive.'

  def __init__(self, arcname, content, mode):
    self._arcname = arcname
    self._content = content
    self._mode = mode
               
  #@abstractmethod
  def execute(self, temp_dir):
    'Execute this operation in a temp_dir of the unpacked archive.'
    file_util.save(path.join(temp_dir, self._arcname), content = self._content, mode = self._mode)

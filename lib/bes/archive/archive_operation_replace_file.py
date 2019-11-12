#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_util import file_util
from bes.common.check import check

from .archive_operation_base import archive_operation_base

class archive_operation_replace_file(archive_operation_base):
  'Add a file to an archive.'

  def __init__(self, arcname, replacement):
    self._arcname = arcname
    self._replacement = replacement
               
  #@abstractmethod
  def execute(self, temp_dir):
    'Execute this operation in a temp_dir of the unpacked archive.'
    file_util.copy(self._replacement, path.join(temp_dir, self._arcname))

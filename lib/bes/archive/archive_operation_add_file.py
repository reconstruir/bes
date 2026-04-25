#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.files.bf_file_ops import bf_file_ops
from ..system.check import check

from .archive_operation_base import archive_operation_base

class archive_operation_add_file(archive_operation_base):
  'Add a file to an archive.'

  def __init__(self, arcname, content, perm):
    self._arcname = arcname
    self._content = content
    self._perm = perm
               
  #@abstractmethod
  def execute(self, temp_dir):
    'Execute this operation in a temp_dir of the unpacked archive.'
    bf_file_ops.save(path.join(temp_dir, self._arcname), content = self._content, perm = self._perm)

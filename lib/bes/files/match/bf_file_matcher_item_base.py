#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bf_file_type import bf_file_type
from ..bf_path_type import bf_path_type

from .bf_file_matcher_item_i import bf_file_matcher_item_i

class bf_file_matcher_item_base(bf_file_matcher_item_i):

  _log = logger('bf_file_matcher')
  
  def __init__(self, file_type, path_type):
    file_type = check.check_bf_file_type(file_type, allow_none = True)
    path_type = check.check_bf_path_type(path_type, allow_none = True)

    self._file_type = file_type
    self._path_type = path_type

  @property
  def file_type(self):
    return self._file_type

  @property
  def path_type(self):
    return self._path_type
  
  def match_file_type(self, entry):
    'Return True if the entry file type matches.'
    check.check_bf_entry(entry)

    if self._file_type != None:
      matched = self._file_type.mask_matches(entry.file_type)
    else:
      matched = True
    #self._log.log_d(f'{self}: match_file_type({entry.relative_filename}) file_type="{self._file_type}" => {matched}')
    return matched

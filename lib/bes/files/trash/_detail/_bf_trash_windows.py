#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import ctypes

from bes.system.log import logger

from ._bf_trash_i import _bf_trash_i

class _bf_trash_windows(_bf_trash_i):

  _log = logger('bf_trash')
  
  @classmethod
  #@abstractmethod
  def empty_trash(clazz):
    'Empty the trash.'
    # Constants for the SHEmptyRecycleBin function
    SHERB_NOCONFIRMATION = 0x00000001
    SHERB_NOPROGRESSUI = 0x00000002
    SHERB_NOSOUND = 0x00000004

    # Call the SHEmptyRecycleBin function
    result = ctypes.windll.shell32.SHEmptyRecycleBinW(
      None,  # hWnd (optional, can be None)
      None,  # pszRootPath (optional, can be None to target all drives)
      SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
    )

    # Check the result
    if result != 0:
      clazz._log.log_e(f'Failed to empty Recycle Bin. Error code: {result}')
    else:
      clazz._log.log_i('Recycle Bin successfully emptied.')

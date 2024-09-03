#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib

from bes.system.check import check
from bes.system.log import logger

from ..bf_check import bf_check

class bf_checksum(object):

  _log = logger('bf_checksum')
  
  # https://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
  @classmethod
  def checksum(clazz, filename, function_name, chunk_size = None, num_chunks = None):
    filename = bf_check.check_file(filename)
    check.check_string(function_name)
    check.check_int(chunk_size, allow_none = True)
    check.check_int(num_chunks, allow_none = True)
    
    clazz._log.log_method_d()
    chunk_size = chunk_size or (1024 * 1024)
    hasher = hashlib.new(function_name)
    with open(filename, 'rb') as fin: 
      for chunk_index, chunk in enumerate(iter(lambda: fin.read(chunk_size), b''), start = 1):
        hasher.update(chunk)
        if num_chunks == chunk_index:
          break
#        print(f'chunk_size={chunk_size} chunk_number={chunk_number} num_chunks={num_chunks}')
    return hasher.hexdigest()

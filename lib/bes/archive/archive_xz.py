#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .archive_tar import archive_tar

class archive_xz(archive_tar):
  'XZ archive.'

  # https://tukaani.org/xz/xz-file-format.txt
  _MAGIC = b'\xfd\x37\x7a\x58\x5a\x00'
  
  def __init__(self, filename):
    super(archive_xz, self).__init__(filename)

  @classmethod
  #@abstractmethod
  def name(clazz, filename):
    'Name of this archive format.'
    return 'xz'
    
  @classmethod
  #@abstractmethod
  def file_is_valid(clazz, filename):
    with open(filename, 'rb') as fin:
      magic = fin.read(len(clazz._MAGIC))
      return magic == clazz._MAGIC

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.string_util import string_util
from bes.system.check import check
from bes.fs.file_check import file_check
from bes.system.execute import execute
from bes.system.host import host
from bes.system.which import which

from ._file_mime_type_detector_base import _file_mime_type_detector_base

class _file_mime_type_detector_file_exe(_file_mime_type_detector_base):

  @classmethod
  #@abstractmethod
  def is_supported(clazz):
    'Return True if this class is supported on the current platform.'
    return host.is_unix() and which.which('file') != None
  
  @classmethod
  #@abstractmethod
  def detect_mime_type(clazz, filename):
    'Detect the mime type for file.'
    filename = file_check.check_file(filename)

    cmd = [ 'file', '--brief', '--mime', string_util.quote_if_needed(filename) ]
    if not path.isfile(filename):
      raise IOError('file not found: "{}"'.format(filename))
    rv = execute.execute(cmd, raise_error = False, quote = True)
    if rv.exit_code != 0:
      return None
    text = rv.stdout.strip()
    lines = text.splitlines()
    if not lines:
      return None
    parts = lines[0].split(';')
    if not parts:
      return None
    return parts[0].strip()

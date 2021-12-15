#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.execute import execute

class file_mime_type_unix_file_exe(object):
  'Detect mime types using the file utility on unix.'
    
  @classmethod
  def mime_type(clazz, filename):
    cmd = [ 'file', '--brief', '--mime', filename ]
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

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.fs.file_check import file_check
from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_options import file_resolver_options
from bes.fs.file_mime import file_mime
from bes.system.python import python
from bes.fs.filename_util import filename_util

class refactor_files(object):

  @classmethod
  def resolve_python_files(clazz, files):
    'Resolve python files.'
    
    def _match_function(filename):
      if not file_mime.is_text(filename):
        return False
      if python.is_python_script(filename):
        return True
      return filename_util.has_extension(filename.lower(), 'py')
    options = file_resolver_options(match_function = _match_function,
                                    match_basename = False)
    resolved = file_resolver.resolve_files(files, options = options)
    return resolved.files()

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.algorithm import algorithm
from bes.fs.file_check import file_check
from bes.fs.file_mime import file_mime
from bes.fs.file_path import file_path
from bes.fs.file_find import file_find
from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_options import file_resolver_options
from bes.fs.file_search import file_search
from bes.fs.file_util import file_util
from bes.fs.filename_util import filename_util
from bes.system.python import python

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

  @classmethod
  def search_files(clazz, files, text, word_boundary = False, ignore_case = False):
    'Search for text in files.'
    
    result = []
    for filename in files:
      next_matches = file_search.search_file(filename, text,
                                             word_boundary = word_boundary,
                                             ignore_case = ignore_case)
      result.extend(next_matches)
    return sorted(algorithm.unique([ item.filename for item in result ]))

  @classmethod
  def rename_dirs(clazz, src_pattern, dst_pattern, root_dir, word_boundary = False):
    assert src_pattern
    assert dst_pattern
    assert not src_pattern in dst_pattern
    assert not dst_pattern in src_pattern
    
    root_dir = path.abspath(root_dir)
    file_check.check_dir(root_dir)
    while True:
      dirs = file_find.find(root_dir, relative = True, file_type = file_find.DIR)
      dirs = [ d for d in dirs if src_pattern in d ]
      dirs = clazz._minimum_paths(dirs, src_pattern)
      if not dirs:
        return
      src_dir = dirs[0]
      dst_dir = src_dir.replace(src_pattern, dst_pattern)
      file_util.rename(src_dir, dst_dir)

  @classmethod
  def _minimum_path(clazz, p, src_pattern):
    v = file_path.split(p)
    result = []
    for x in v:
      result.append(x)
      if src_pattern in x:
        break
    return file_path.join(result)

  @classmethod
  def _minimum_paths(clazz, paths, src_pattern):
    return algorithm.unique([ clazz._minimum_path(p, src_pattern) for p in paths ])
  

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.file_find import file_find
from bes.common.algorithm import algorithm
from bes.common.object_util import object_util

class file_finder(object):

  @classmethod
  def find_python_files(clazz, d):
    return file_find.find_fnmatch(d, [ '*.py' ], relative = False)

  @classmethod
  def find_tests(clazz, d):
    return file_find.find_fnmatch(d, [ '*test_*.py' ], relative = False)

  @classmethod
  def find_python_compiled_files(clazz, dirs):
    dirs = object_util.listify(dirs)
    result = []
    for d in dirs:
      result.extend(file_find.find_fnmatch(d, [ '*.pyc' ], relative = False))
    return algorithm.unique(result)

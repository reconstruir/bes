#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.bcli.bcli_application import bcli_application
from bes.common.object_util import object_util
from bes.files.bf_check import bf_check
from bes.files.find.bf_file_finder import bf_file_finder
from bes.system.check import check

class bes_file_application(bcli_application):

  def resolve_files(self, what, func=None):
    '''
    Return a sorted list of absolute filenames for what.
    what can be one or more files or directories (searched recursively).
    '''
    check.check_callable(func, allow_none=True)
    if not what:
      return []
    what = object_util.listify(what)
    result = []
    for x in what:
      result.extend(self._resolve_one(x))
    result = sorted(set(result))
    if func:
      result = [f for f in result if func(f)]
    return result

  def _resolve_one(self, filename):
    filename = path.abspath(filename)
    if path.isfile(filename):
      return [filename]
    elif path.isdir(filename):
      finder = bf_file_finder()
      return finder.find(filename).entries.absolute_filenames(sort=True)
    if path.exists(filename):
      raise RuntimeError('Not a file or directory: {}'.format(filename))
    raise RuntimeError('File not found: {}'.format(filename))

  def resolve_file(self, filename, root_dir=None):
    if root_dir:
      return path.join(root_dir, filename)
    if '~' in filename:
      filename = path.expanduser(filename)
    if not path.isabs(filename):
      filename = path.abspath(filename)
    return filename

  def resolve_dir(self, dirname, root_dir=None):
    return self.resolve_file(dirname, root_dir=root_dir)

  def check_file(self, filename):
    bf_check.check_file(filename)

  def check_dir(self, dirname):
    bf_check.check_dir(dirname)

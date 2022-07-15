#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, os.path as path
from collections import namedtuple
from bes.system.check import check
from bes.fs.file_check import file_check
from bes.fs.file_util import file_util

from .config_data import config_data

class config_file(namedtuple('config_file', 'root_dir, filename, data')):

  def __new__(clazz, filename):
    filename = path.abspath(filename)
    check.check_string(filename)
    file_check.check_file(filename)
    content = file_util.read(filename, codec = 'utf-8')
    root_dir = path.normpath(path.join(path.dirname(filename), '..'))
    data = config_data.parse(content, filename = filename)
    return clazz.__bases__[0].__new__(clazz, root_dir, filename, data)

  def substitute(self, variables):
    variables = copy.deepcopy(variables)
    variables['root_dir'] = self.root_dir
    return self.__class__.__bases__[0].__new__(self.__class__,
                                               self.root_dir,
                                               self.filename,
                                               self.data.substitute(variables))

  @property
  def nice_filename(self):
    home = path.expanduser('~/')
    return self.filename.replace(home, '~/')

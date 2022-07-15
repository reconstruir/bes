# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from bes.fs.file_ignore import file_ignore_item
from bes.fs.temp_file import temp_file

class git_ignore(object):
  'A class to deal with .gitignore files.'

  @classmethod
  def read_gitignore_file(clazz, root_dir):
    'Return the contents of an .gitignore file in root_dir or None if it does not exist.'
    p = path.join(root_dir, '.gitignore')
    if not path.isfile(p):
      return None
    return clazz.read_ignore_file(p)
  
  @classmethod
  def read_ignore_file(clazz, filename):
    'Return the contents of an ignore file with comments stripped.'
    return file_ignore_item.read_file(filename).patterns

  @classmethod
  def read_gitignore_text(clazz, text):
    'Return the contents of .gitignore with comments stripped from text.'

    tmp = temp_file.make_temp_file(content = text, suffix = '.gitignore')
    return clazz.read_ignore_file(tmp)

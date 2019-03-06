#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .repo import repo
from bes.common import check
from bes.fs import temp_file

class temp_git_repo(object):
  'A class to deal with tmp git repos mostly for testing.'

  @classmethod
  def make_temp_repo(clazz, init_args = None, content = None, debug = False):
    tmp_dir = temp_file.make_temp_dir(delete = not debug)
    if debug:
      print('make_temp_repo: tmp_dir: %s' % (tmp_dir))
    r = repo(tmp_dir, address = None)
    init_args = init_args or []
    r.init(*init_args)
    if content:
      check.check_string_seq(content)
      r.write_temp_content(content, commit = True)
    return r

  @classmethod
  def make_temp_cloned_repo(clazz, address, debug = False):
    tmp_dir = temp_file.make_temp_dir(delete = not debug)
    if debug:
      print('make_temp_cloned_repo: tmp_dir: %s' % (tmp_dir))
    r = repo(tmp_dir, address = address)
    r.clone()
    return r

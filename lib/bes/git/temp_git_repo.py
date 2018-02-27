#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .repo import repo
from bes.common import check
from bes.fs import temp_file

class temp_git_repo(object):
  'A class to deal with tmp git repos mostly for testing.'

  @classmethod
  def make_temp_repo(clazz, content = None):
    tmp_dir = temp_file.make_temp_dir()
    r = repo(tmp_dir, address = None)
    r.init()
    if content:
      check.check_string_seq(content)
      r.write_temp_content(content)
      r.add('.')
      r.commit('add temp repo content', '.')
    return r

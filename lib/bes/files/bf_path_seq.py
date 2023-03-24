#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..common.object_util import object_util
from ..system.check import check

from .bf_filename import bf_filename

class bf_path_seq(object):
  'bf_path_seq'

  @classmethod
  def make_paths_absolute(clazz, paths):
    paths = object_util.listify(paths)
    return [ path.abspath(p) for p in paths ]

  @classmethod
  def make_paths_relative(clazz, paths):
    paths = object_util.listify(paths)
    return [ path.relpath(p) for p in paths ]

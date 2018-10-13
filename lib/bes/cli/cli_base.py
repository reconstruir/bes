#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os, os.path as path

from bes.fs import file_util

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class cli_base(object):

  def __init__(self):
    pass

  @classmethod
  def check_file_exists(clazz, filename, label = 'file'):
    if not path.isfile(filename):
      raise RuntimeError('%s not found: %s' % (label, filename))

  @classmethod
  def check_dir_exists(clazz, d, label = 'dir'):
    if not path.isdir(d):
      raise RuntimeError('%s not found: %s' % (label, d))

  @classmethod
  def resolve_filename(clazz, filename):
    return file_util.ensure_abspath(filename)

  @classmethod
  def add_verbose_option(clazz, parser):
    parser.add_argument('-v',
                        '--verbose',
                        action = 'store_true',
                        default = False,
                        help = 'Be verbose about what is happening [ False ]')

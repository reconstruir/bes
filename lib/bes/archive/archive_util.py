#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs.temp_file import temp_file
from bes.fs.file_util import file_util
from bes.common.object_util import object_util

from .archiver import archiver

class archive_util(object):
  'Archive util.'

  @classmethod
  def remove_members(clazz, archive, members, debug = False):
    members = object_util.listify(members)
    tmp_dir = archiver.extract_all_temp_dir(archive, delete = not debug)
    if debug:
      print('tmp_dir: {}'.format(tmp_dir))
    members = [ path.join(tmp_dir, m) for m in members ]
    file_util.remove(members)
    archiver.create(archive, tmp_dir)

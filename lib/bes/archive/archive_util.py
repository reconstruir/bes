#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs.temp_file import temp_file
from bes.fs.file_util import file_util
from bes.common.object_util import object_util
from bes.common.dict_util import dict_util

from .archiver import archiver

class archive_util(object):
  'Archive util.'

  @classmethod
  def remove_members(clazz, archive, members, debug = False):
    'Remove memvers from an archive and then recreate it.'
    members = object_util.listify(members)
    tmp_dir = archiver.extract_all_temp_dir(archive, delete = not debug)
    if debug:
      print('tmp_dir: {}'.format(tmp_dir))
    members = [ path.join(tmp_dir, m) for m in members ]
    file_util.remove(members)
    archiver.create(archive, tmp_dir)

  @classmethod
  def duplicate_members(clazz, archives):
    '''
    Return a dict of members in archives that are duplicates in this form:
    {
      'foo.txt': { 'archive1.zip', 'archive2.zip' },
      'bar.txt': { 'archive3.zip', 'archive4.zip', 'archive5.zip' },
    }
    '''
    counts = {}
    archive_to_members = {}
    for archive in archives:
      archive_to_members[archive] = set(archiver.members(archive))
      
    for archive in archives:
      for member in archive_to_members[archive]:
        if not member in counts:
          counts[member] = 1
        else:
          counts[member] += 1
    result = {}
    for key, value in counts.items():
      if value > 1:
        if key not in result:
          result[key] = set()
        for archive, members in archive_to_members.items():
          if key in members:
            result[key].add(archive)
    return result

  @classmethod
  def member_checksums(clazz, archive, members, debug = False):
    'Return a dict of checksums for the given members in archive.'
    members = object_util.listify(members)
    tmp_dir = archiver.extract_all_temp_dir(archive, delete = not debug)
    if debug:
      print('tmp_dir: {}'.format(tmp_dir))
    result = {}
    for member in members:
      assert not member in result
      p = path.join(tmp_dir, member)
      if not path.exists(p):
        raise IOError('member not found: {}'.format(member))
      if not path.isfile(p):
        raise IOError('member is not a file: {}'.format(member))
      result[member] = file_util.checksum('sha256', path.join(tmp_dir, member))
    return result

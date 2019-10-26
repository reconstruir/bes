#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint
import os.path as path
from bes.fs.temp_file import temp_file
from bes.fs.file_util import file_util
from bes.fs.file_match import file_match
from bes.common.object_util import object_util
from bes.common.dict_util import dict_util
from bes.text.text_line_parser import text_line_parser

from .archiver import archiver

class archive_util(object):
  'Archive util.'

  @classmethod
  def remove_members(clazz, archive, members, debug = False):
    'Remove members from an archive and then recreate it.'
    members = object_util.listify(members)
    tmp_dir = archiver.extract_all_temp_dir(archive, delete = not debug)
    if debug:
      print('tmp_dir: {}'.format(tmp_dir))
    members = [ path.join(tmp_dir, m) for m in members ]
    file_util.remove(members)
    archiver.create(archive, tmp_dir)

  @classmethod
  def remove_members_matching_patterns(clazz, archive, patterns, debug = False):
    'Remove members that match any of the given patterns.'
    members = clazz.match_members(archive, patterns)
    return clazz.remove_members(archive, members, debug = debug)

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
    
  @classmethod
  def duplicate_members(clazz, archives, only_content_conficts = False):
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

    if only_content_conficts:
      result = clazz._dups_only_with_conficts(result)
            
    return result

  @classmethod
  def _dups_only_with_conficts(clazz, dups):
    'Filter out dups that have the same content.'
    result = {}
    for member, archives in dups.items():
      if clazz._has_conflict(archives, member):
        result[member] = archives
    return result

  @classmethod
  def _has_conflict(clazz, archives, member):
    'Return True if any archive in archives has a content conflict with member.'
    checksum = None
    assert(archives)
    assert(member)
    for archive in archives:
      next_checksum = archiver.member_checksum(archive, member)
      if checksum is None:
        checksum = next_checksum
      else:
        if next_checksum != checksum:
          return True
    return False
  
  @classmethod
  def combine(clazz, archives, dest_archive, check_content = False,
              base_dir = None, exclude = None):
    '''
    Combine a list of archives into one.  If check content is True and 
    there are content dups with different checksums, an error will
    be raised.
    '''
    exclude = exclude or []
    if check_content:
      dups = clazz.duplicate_members(archives, only_content_conficts = True)
      if exclude:
        for next_exclude in exclude:
          if next_exclude in dups:
            del dups[next_exclude]
      if dups:
        raise RuntimeError('Archives have duplicate members with different content\n{}.'.format(pprint.pformat(dups)))

    tmp_dir = temp_file.make_temp_dir()
    for archive in archives:
      archiver.extract_all(archive, tmp_dir)
    archiver.create(dest_archive, tmp_dir, base_dir = base_dir, exclude = exclude)

  @classmethod
  def match_members(clazz, archive, patterns):
    'Return a list of members that match any pattern in patterns.'
    return file_match.match_fnmatch(archiver.members(archive), patterns, file_match.ANY, basename = False)

  @classmethod
  def read_patterns(clazz, filename):
    'Return a list of members that match any pattern in patterns.'
    text = file_util.read(filename)
    return text_line_parser.parse_lines(text)

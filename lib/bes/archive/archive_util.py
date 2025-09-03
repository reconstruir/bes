#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint
import os.path as path

from collections import namedtuple

from bes.common.dict_util import dict_util
from bes.common.object_util import object_util
from bes.fs.file_match import file_match
from bes.files.bf_path import bf_path
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.execute import execute
from bes.system.log import logger
from bes.system.which import which
from bes.text.text_line_parser import text_line_parser

from .archiver import archiver

class archive_util(object):
  'Archive util.'

  _log = logger('archive_util')
  
  @classmethod
  def remove_members(clazz, archive, members, debug = False):
    'Remove members from an archive and then recreate it.'
    members = object_util.listify(members)
    tmp_dir = archiver.extract_all_temp_dir(archive, delete = not debug)
    if debug:
      print('tmp_dir: {}'.format(tmp_dir))
    members = [ path.normpath(path.join(tmp_dir, m)) for m in members ]
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
    clazz._log.log_method_d()
    if check_content:
      dups = clazz.duplicate_members(archives, only_content_conficts = True)
      clazz._log.log_d('combine: dups={}'.format(dups))
      if exclude:
        for next_exclude in exclude:
          clazz._log.log_d('combine: checking next_exclude={} vs exclude={}'.format(next_exclude, exclude))
          if next_exclude in dups:
            clazz._log.log_d('combine: {}'.format(next_exclude))
            del dups[next_exclude]
      clazz._log.log_d('combine: dups={}'.format(dups))
      if dups:
        raise RuntimeError('Archives have duplicate members with different content\n{}.'.format(pprint.pformat(dups)))

    tmp_dir = temp_file.make_temp_dir()
    for archive in archives:
      archiver.extract_all(archive, tmp_dir)
    archiver.create(dest_archive, tmp_dir, base_dir = base_dir, exclude = bf_path.xp_path_list(exclude))

  @classmethod
  def match_members(clazz, archive, patterns):
    'Return a list of members that match any pattern in patterns.'
    return file_match.match_fnmatch(archiver.members(archive), patterns, file_match.ANY, basename = False)

  @classmethod
  def read_patterns(clazz, filename):
    'Return a list of members that match any pattern in patterns.'
    text = file_util.read(filename, codec = 'utf8')
    return text_line_parser.parse_lines(text).to_list()

    
  @classmethod
  def search(clazz, tarball, pattern, ignore_case = False, whole_word = False):
    'Return the output of either ag (silver searcher) or grep for the contents of an archive.'
    ag = which.which('ag')
    if ag:
      cmd = [ ag ]
    else:
      grep = which.which('grep')
      if not grep:
        raise RuntimeError('No grep or ag found.')
      cmd = [ grep, '-r' ]

    if ignore_case:
      cmd.append('-i')
    if whole_word:
      cmd.append('-w')
    cmd.extend([ pattern, '.' ])
      
    tmp_dir = temp_file.make_temp_dir()
    archiver.extract(tarball, tmp_dir, strip_common_ancestor = True)
    result = execute.execute(cmd, cwd = tmp_dir, shell = True, raise_error = False)
    file_util.remove(tmp_dir)
    return result

  @classmethod
  def diff_manifest(clazz, archive1, archive2, strip_common_ancestor = False):
    'Return the output of diffing the contents of 2 archives.'
    members1 = archiver.members(archive1)
    members2 = archiver.members(archive2)
    content1 = '\n'.join(members1)
    content2 = '\n'.join(members2)
    tmp_file1 = temp_file.make_temp_file(content = content1)
    tmp_file2 = temp_file.make_temp_file(content = content2)
    cmd = [ 'diff', '-u', '-r', tmp_file1, tmp_file2 ]
    rv = execute.execute(cmd, raise_error = False, stderr_to_stdout = True)
    return rv

  @classmethod
  def diff_contents(clazz, archive1, archive2, strip_common_ancestor = False):
    'Return the output of diffing the contents of 2 archives.'
    tmp_dir = temp_file.make_temp_dir(delete = True)
    tmp_dir1 = path.join(tmp_dir, 'a')
    tmp_dir2 = path.join(tmp_dir, 'b')
    archiver.extract_all(archive1, tmp_dir1, strip_common_ancestor = strip_common_ancestor)
    archiver.extract_all(archive2, tmp_dir2, strip_common_ancestor = strip_common_ancestor)
    cmd = [ 'diff', '-u', '-r', tmp_dir1, tmp_dir2 ]
    rv = execute.execute(cmd, raise_error = False, stderr_to_stdout = True)
    return rv

  _diff_dir_result = namedtuple('_diff_dir_result', 'filename, archive1, archive2, execute_result')
  @classmethod
  def diff_dir(clazz, dir1, dir2, strip_common_ancestor = False):
    'Return the output of diffing all archives found in 2 directories.'

    archives1 = archiver.find_archives(dir1)
    archives2 = archiver.find_archives(dir2)

    if archives1 != archives2:
      return 1

    archives1_abs = [ path.join(dir1, f) for f in archives1 ]
    archives2_abs = [ path.join(dir2, f) for f in archives2 ]

    result = []
    for archive_rel, archive1_abs, archive2_abs in zip(archives1, archives1_abs, archives2_abs):
      rv = clazz.diff_contents(archive1_abs, archive2_abs, strip_common_ancestor = strip_common_ancestor)
      result.append(clazz._diff_dir_result(archive_rel, archive1_abs, archive2_abs, rv))
    return result

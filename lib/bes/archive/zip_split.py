#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import zipfile
from collections import namedtuple

from bes.common.check import check
from bes.fs.file_util import file_util
from bes.system.log import logger

from .archiver import archiver

class zip_split(object):
  'Split zip files by maximum size.'

  log = logger('zip_split')
  
  @classmethod
  def split(clazz, archive, max_size):
    format_name = archiver.format_name(archive)

    if format_name != 'zip':
      raise RuntimeError('format not supported for split: {} - should be zip'.format(format_name))

    archive_size = file_util.size(archive)
    
    clazz.log.log_d('split: archive={} max_size={} archive_size={}'.format(archive,
                                                                           file_util.format_size(max_size),
                                                                           file_util.format_size(archive_size)))
    
    info = clazz._read_info(archive)
    old_size = 0

#    for filename, member_info in info.members.items():
#      if len(member_info) != 1:
#        if len(set(member_info)) != 1:
#          for dup in member_info:
#            print('duplicate member: {}'.format(dup.CRC))

    split_buckets = []
    current_bucket = []
    
    for filename, member_info in sorted(info.members.items()):
      next_info = member_info[0]
      new_size = old_size + next_info.compress_size

      clazz.log.log_d('split: before: arcname={} new_size={} old_size={} current_bucket={} split_buckets={}'.format(filename,
                                                                                                                    file_util.format_size(new_size),
                                                                                                                    file_util.format_size(old_size),
                                                                                                                    current_bucket,
                                                                                                                    split_buckets))
      
      if new_size > max_size:
        split_buckets.append(current_bucket)
        current_bucket = []
        current_bucket.append(next_info.filename)
        old_size = 0
      else:
        current_bucket.append(next_info.filename)
        old_size = new_size

      clazz.log.log_d('split:  after: arcname={} new_size={} old_size={} current_bucket={} split_buckets={}'.format(filename,
                                                                                                                    file_util.format_size(new_size),
                                                                                                                    file_util.format_size(old_size),
                                                                                                                    current_bucket,
                                                                                                                    split_buckets))
      
        
    # Deal with the last bucket if not empty
    if current_bucket:
      split_buckets.append(current_bucket)

    tmp_dir = archiver.extract_all_temp_dir(archive)
    split_file_list = []
    for i, bucket in enumerate(split_buckets):
      next_filename = clazz._make_split_filename(archive, i + 1, len(split_buckets))
      archiver.create(next_filename, tmp_dir, include = bucket)
      split_file_list.append(next_filename)
    return split_file_list

  _archive_info = namedtuple('_archive_info', 'infos, members')
  @classmethod
  def _read_info(clazz, archive):
    with zipfile.ZipFile(archive, mode = 'r') as arc:
      infos = arc.infolist()
      infos = sorted(infos, key = lambda info: info.filename)
      members = {}
      for info in infos:
        if info.filename not in members:
          members[info.filename] = []
        members[info.filename].append(info)
      return clazz._archive_info(infos, members)

  @classmethod
  def _make_split_filename(clazz, filename, index, total):
    no_ext = file_util.remove_extension(filename)
    ext = file_util.extension(filename)
    index_s = str(index).zfill(2)
    total_s = str(total).zfill(2)
    return '{}.{}of{}.{}'.format(no_ext, index_s, total_s, ext)

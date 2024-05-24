#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path
import math

from bes.archive.archiver import archiver
from bes.system.check import check
from bes.common.time_util import time_util
from bes.system.check import check
from bes.system.log import logger

from ..bf_dir import bf_dir
from ..bf_entry import bf_entry
from ..bf_file_ops import bf_file_ops
from ..bf_filename import bf_filename
from ..match.bf_match import bf_match
from ..temp.bf_temp_file import bf_temp_file

from .bf_split_error import bf_split_error
from .bf_split_options import bf_split_options

from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_item_list import file_resolver_item_list
from bes.fs.file_resolver_options import file_resolver_options

class bf_split(object):
  'A class to find duplicate files'

  _log = logger('bf_split')

  _UNSPLIT_EXTENSIONS = [ '01', '001', '0001', '00001' ]
  @classmethod
  def _match_unsplit_files(clazz, filename):
    return bf_filename.has_any_extension(filename, clazz._UNSPLIT_EXTENSIONS)
  
  @classmethod
  def find_and_unsplit(clazz, files, options = None):
    check.check_string_seq(files)
    check.check_bf_split_options(options, allow_none = True)

    info = clazz.find_and_unsplit_info(files, options = options)
    for item in info.items:
      item_target = item.target
      options.blurber.blurb_verbose(f'Unsplitting {item_target} - {len(item.files)} parts.')
      tmp = bf_temp_file.make_temp_file(prefix = path.basename(item_target),
                                        dir = path.dirname(item_target),
                                        create = False)
      clazz.unsplit_files(tmp, item.files)
      if options.unzip:
        if archiver.is_valid(tmp):
          members = archiver.members(tmp)
          num_members = len(members)
          if num_members != 1:
            options.blurber.blurb(f'{item_target} archive should have exactly 1 member instead of {num_members}')
          else:
            archive_filename = members[0]
            archive_tmp_dir = bf_temp_file.make_temp_dir(prefix = path.basename(archive_filename),
                                                         dir = path.dirname(item_target),
                                                         delete = False)
            archiver.extract_all(tmp, archive_tmp_dir)
            archive_tmp_file = path.join(archive_tmp_dir, archive_filename)
            assert path.exists(archive_tmp_file)
            bf_file_ops.rename(archive_tmp_file, tmp)
            bf_file_ops.remove(archive_tmp_dir)
            item_target = path.join(path.dirname(item_target), archive_filename)
            
      target = None
      if path.exists(item_target):
        if bf_file_ops.files_are_the_same(tmp, item_target):
          options.blurber.blurb(f'{item_target} already exists and is the same')
          bf_file_ops.remove(tmp)
        else:
          ts = time_util.timestamp(delimiter = '',
                                   milliseconds = False,
                                   when = options.existing_file_timestamp)
          target = clazz._make_timestamp_filename(item_target, ts)
          options.blurber.blurb(f'{item_target} already exists but is different.  Renaming to {target}')
      else:
        target = item_target
      if target:
        bf_file_ops.rename(tmp, target)
      bf_file_ops.remove(item.files)

  @classmethod
  def _make_timestamp_filename(clazz, filename, ts):
    dirname = path.dirname(filename)
    basename = path.basename(filename)
    basename_without_extension = bf_filename.without_extension(basename)
    ext = bf_filename.extension(basename)
    new_basename = bf_filename.add_extension(f'{basename_without_extension}-{ts}', ext)
    return path.join(dirname, new_basename)
      
  _split_item = namedtuple('_split_item', 'target, files')
  _split_result = namedtuple('_find_duplicates_result', 'items, resolved_files')
  @classmethod
  def find_and_unsplit_info(clazz, files, options = None):
    check.check_string_seq(files)
    check.check_bf_split_options(options, allow_none = True)

    options = options or bf_split_options()
    resolver_options = file_resolver_options(recursive = options.recursive,
                                             match_basename = True,
                                             match_function = clazz._match_unsplit_files)
    resolved_files = file_resolver.resolve_files(files, options = resolver_options)
    items = []
    for f in resolved_files:
      item = clazz._unsplit_one_info(f.filename_abs, options)
      if item:
        items.append(item)
    return clazz._split_result(items, resolved_files)
      
  @classmethod
  def _unsplit_one_info(clazz, first_filename, options):
    files_group = clazz._files_group(first_filename, options.ignore_extensions)
    if len(files_group) == 1:
      return None
    if options.check_downloading_extension:
      dl_files = clazz._files_group_is_still_downloading(files_group, options.check_downloading_extension)
      if dl_files:
        for f in dl_files:
          options.blurber.blurb(f'Still downloading: {f}')
        return None
    if not clazz._files_group_is_complete(files_group):
      if options.ignore_incomplete:
        print('Ignoring incomplete group:\n  {}'.format('\n  '.join(files_group)))
        return None
      else:
        raise bf_split_error('Incomplete group:\n  {}'.format('\n  '.join(files_group)))
    
    target_filename = bf_filename.without_extension(first_filename)
    return clazz._split_item(target_filename, files_group)
    
  @classmethod
  def _files_group(clazz, first_filename, ignore_extensions):
    def _is_group_file(filename):
      return clazz._is_group_file(first_filename, filename, ignore_extensions)
    files = bf_dir.list(path.dirname(first_filename), function = _is_group_file)
    assert len(files) > 0
    assert files[0] == first_filename
    return files

  @classmethod
  def _is_group_file(clazz, first_filename, filename, ignore_extensions):
    first_basename = path.basename(first_filename)
    first_basename_without_extension = bf_filename.without_extension(first_basename)
    first_ext = bf_filename.extension(first_basename)
    first_ext_len = len(first_ext)

    if ignore_extensions and bf_filename.has_any_extension(filename,
                                                             ignore_extensions,
                                                             ignore_case = True):
      filename = bf_filename.without_extension(filename)
    
    basename = path.basename(filename)
    basename_without_extension = bf_filename.without_extension(basename)
    ext = bf_filename.extension(basename)
    if not ext:
      return False
    ext_len = len(ext)
    if basename_without_extension != first_basename_without_extension:
      return False
    if ext_len != first_ext_len:
      return False
    return ext.isdigit()

  @classmethod
  def _files_group_is_complete(clazz, files):
    last_ext = bf_filename.extension(files[-1])
    last_index = int(last_ext)
    return len(files) == last_index

  @classmethod
  def _files_group_is_still_downloading(clazz, files, downloading_extension):
    result = []
    for filename in files:
      downloading_sentinel = bf_filename.add_extension(filename, downloading_extension)
      if path.exists(downloading_sentinel):
        result.append(filename)
    return result
  
  @classmethod
  def split_file(clazz, filename, chunk_size, zfill_length = None, output_directory = None):
    check.check_string(filename)
    check.check_int(chunk_size)
    check.check_int(zfill_length, allow_none = True)
    
    file_size = bf_entry(filename).size
    
    clazz._log.log_method_d()
    
    num_total = int(math.ceil(float(file_size) / float(chunk_size)))
    result_file_list = []
    zfill_length = zfill_length or len(str(num_total))
    output_directory = output_directory or path.dirname(filename)
    with open(filename, 'rb') as fin:
      index = 0
      while True:
        data = fin.read(chunk_size)
        if not data:
          break
        next_filename = clazz._make_split_filename(filename,
                                                   output_directory,
                                                   index + 1,
                                                   zfill_length)
        with open(next_filename, 'wb') as fout:
          fout.write(data)
          result_file_list.append(next_filename)
        index += 1
    return result_file_list

  @classmethod
  def _make_split_filename(clazz, filename, output_directory, index, zfill_length):
    basename = path.basename(filename)
    split_filename = path.join(output_directory, basename)
    extension = str(index).zfill(zfill_length)
    return bf_filename.add_extension(split_filename, extension)
  
  @classmethod
  def unsplit_files(clazz, target_filename, files, buffer_size = 1024 * 1204):
    with open(target_filename, 'wb') as fout:
      for next_filename in files:
        with open(next_filename, 'rb') as fin:
          while True:
            data = fin.read(buffer_size)
            if not data:
              break
            fout.write(data)
  
  @classmethod
  def is_split_filename(clazz, filename):
    check.check_string(filename)
    
    pattern = '*.[0-9][0-9][0-9]'
    return bf_match.match_fnmatch(filename, pattern, basename = True) != []

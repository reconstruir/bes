#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system import log
from .file_find import file_find
from .file_util import file_util

class file_sync(object):

  @classmethod
  def sync(clazz, src_dir, dst_dir, exclude = None):
    exclude = set(exclude or [])
    src_files = set(file_find.find(src_dir, relative = True, file_type = file_find.FILE))
    src_files = src_files - exclude
    src_dirs = set(file_find.find(src_dir, relative = True, file_type = file_find.DIR))

    dst_files = set(file_find.find(dst_dir, relative = True, file_type = file_find.FILE))
    dst_dirs = set(file_find.find(dst_dir, relative = True, file_type = file_find.DIR))

    files_became_dirs = src_files & dst_dirs
    if files_became_dirs:
      raise RuntimeError('some files became dirs: %s' % (' '.join(files_became_dirs)))
    
    dirs_became_files = dst_files & src_dirs
    if dirs_became_files:
      raise RuntimeError('some dirs became files: %s' % (' '.join(dirs_became_files)))

    # Delete files that went away
    clazz.log_d('SRC: %s' % (src_dir))
    for x in src_files:
      clazz.log_d('  %s' % (x))
    clazz.log_d('DST: %s' % (dst_dir))
    for x in dst_files:
      clazz.log_d('  %s' % (x))
    for dst_file in dst_files:
      if not dst_file in src_files:
        file_util.remove(path.join(dst_dir, dst_file))
        
    # Either copy new files or check a checksum and update them.
    # The reason for the checksum is we want to leave the mtime alone of the content didnt change
    for src_file in src_files:
      src_file_path = path.join(src_dir, src_file)
      dst_file_path = path.join(dst_dir, src_file)
      should_copy = False
      if path.isfile(dst_file_path):
        should_copy = file_util.checksum('sha1', src_file_path) != file_util.checksum('sha1', dst_file_path)
      else:
        should_copy = True
      if should_copy:
        file_util.copy(src_file_path, dst_file_path)
    
log.add_logging(file_sync, 'file_sync')

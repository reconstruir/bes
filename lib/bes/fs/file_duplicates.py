#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from collections import OrderedDict
from os import path

from bes.common.object_util import object_util
from bes.system.check import check
from bes.system.log import logger
from bes.fs.file_check import file_check

from .file_checksum_getter_attributes import file_checksum_getter_attributes
from .file_checksum_getter_db import file_checksum_getter_db
from .file_find import file_find
from .file_util import file_util

class file_duplicates(object):

  _log = logger('file_duplicates')

  DEFAULT_CHECKSUM_DB = path.expanduser('~/.bes/dups/checksum.db')

  _file_checksum_getter_attributes = file_checksum_getter_attributes()
  
  _dup_item = namedtuple('_dup_item', 'filename, duplicates')
  _ordered_filename = namedtuple('_ordered_filename', 'filename, checksum, order')
  @classmethod
  def find_duplicates(clazz, dirs, checksum_db_filename = None):
    assert checksum_db_filename
    dirs = file_check.check_dir_seq(object_util.listify(dirs))
    checksum_db_filename = check.check_string(checksum_db_filename, allow_none = True)
    checksum_db_filename = checksum_db_filename or clazz.DEFAULT_CHECKSUM_DB

    for d in dirs:
      clazz._log.log_d('find_duplicates: dirs: {}'.format(d))
    
    files = []
    for d in dirs:
      files.extend(file_find.find(d, relative = False, file_type = file_find.FILE))
    checksum_to_files = OrderedDict()
    ordered_files = []
    for order, f in enumerate(files):
      checksum = clazz._file_checksum(f, checksum_db_filename)
      if not checksum in checksum_to_files:
        checksum_to_files[checksum] = []
      checksum_to_files[checksum].append(clazz._ordered_filename(f, checksum, order))
      #print('done {} of {}'.format(order + 1, len(files)))

    result = []
    for checksum, ordered_files in checksum_to_files.items():
      if len(ordered_files) > 1:
        sorted_ordered_files = sorted(ordered_files, key = lambda x: x.order)
        filename = sorted_ordered_files[0].filename
        duplicates = [ f.filename for f in sorted_ordered_files[1:] ]
        result.append(clazz._dup_item(filename, duplicates))
    return result

  @classmethod
  def _file_checksum(clazz, filename, checksum_db_filename):
    try:
      getter = file_checksum_getter_attributes()
      return getter.checksum('sha256', filename)
    except PermissionError as ex:
      db = file_checksum_getter_db(checksum_db_filename)
      return db.checksum('sha256', filename)

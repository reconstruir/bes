#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from collections import OrderedDict

from bes.common.object_util import object_util
from bes.system.check import check
from bes.fs.file_check import file_check

from .file_find import file_find
from .file_util import file_util

class file_duplicates(object):

  _dup_item = namedtuple('_find_dups_result', 'filename, duplicates')
  _ordered_filename = namedtuple('_ordered_filename', 'filename, checksum, order')
  @classmethod
  def find_duplicates(clazz, dirs):
    dirs = file_check.check_dir_seq(object_util.listify(dirs))
    files = []
    for d in dirs:
      files.extend(file_find.find(d, relative = False, file_type = file_find.FILE))
    checksum_to_files = OrderedDict()
    ordered_files = []
    for order, f in enumerate(files):
      checksum = file_util.checksum('sha256', f)
      if not checksum in checksum_to_files:
        checksum_to_files[checksum] = []
      checksum_to_files[checksum].append(clazz._ordered_filename(f, checksum, order))

    result = []
    for checksum, ordered_files in checksum_to_files.items():
      if len(ordered_files) > 1:
        sorted_ordered_files = sorted(ordered_files, key = lambda x: x.order)
        filename = sorted_ordered_files[0].filename
        duplicates = [ f.filename for f in sorted_ordered_files[1:] ]
        result.append(clazz._dup_item(filename, duplicates))
    return result

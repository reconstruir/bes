#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check

from .file_resolver_item_list import file_resolver_item_list

class file_duplicates_preparation(namedtuple('file_duplicates_preparation', 'files, resolved_files, dup_checksum_map, options')):

  def __new__(clazz, files, resolved_files, dup_checksum_map, options):
    check.check_string_seq(files)
    check.check_file_resolver_item_list(resolved_files)
    check.check_dict(dup_checksum_map)
    check.check_file_duplicates_options(options)

    return clazz.__bases__[0].__new__(clazz, files, resolved_files, dup_checksum_map, options)
  
check.register_class(file_duplicates_preparation, include_seq = False)

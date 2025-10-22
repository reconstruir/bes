#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from bes.data_classes.bdata_class_list_base import bdata_class_list_base

from .bf_file_dups_finder_item import bf_file_dups_finder_item

class bf_file_dups_finder_item_list(bdata_class_list_base):

  __value_type__ = bf_file_dups_finder_item

bf_file_dups_finder_item_list.register_check_class()

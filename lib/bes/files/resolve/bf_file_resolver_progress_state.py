#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class bf_file_resolver_progress_state(checked_enum):
  SCANNING = 'scanning'
  FINDING = 'resolveing'
  
bf_file_resolver_progress_state.register_check_class()

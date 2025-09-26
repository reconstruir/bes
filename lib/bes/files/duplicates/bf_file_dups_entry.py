#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from bes.files.resolve.bf_file_resolver_entry import bf_file_resolver_entry

class bf_file_dups_entry(bf_file_resolver_entry):

  _log = logger('bf_duplicates')

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
  
check.register_class(bf_file_dups_entry, include_seq = False)

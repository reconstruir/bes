#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import os

from datetime import datetime
from collections import namedtuple

from bes.system.check import check
from bes.system.log import logger
from bes.common.object_util import object_util

from ..bf_check import bf_check
#from ..bf_entry import bf_entry
from ..bf_entry_list import bf_entry_list
#from ..bf_filename import bf_filename
#from ..bf_file_type import bf_file_type
#from ..bf_path_type import bf_path_type
#from ..bf_symlink import bf_symlink
#from ..match.bf_file_matcher_type import bf_file_matcher_type
#from ..match.bf_file_matcher import bf_file_matcher
#
#from .bf_file_resolver_options import bf_file_resolver_options
#from .bf_file_resolver_result import bf_file_resolver_result
#from .bf_file_resolver_stats import bf_file_resolver_stats
#from .bf_walk import bf_walk

from ..find.bf_file_finder_options import bf_file_finder_options
from ..find.bf_file_finder import bf_file_finder

from .bf_file_resolver_entry import bf_file_resolver_entry
from .bf_file_resolver_options import bf_file_resolver_options

class bf_file_resolver(object):

  _log = logger('bf_file_resolver')
  
  def __init__(self, options = None):
    check.check_bf_file_resolver_options(options, allow_none = True)

    self._options = bf_file_resolver_options.clone_or_create(options)
    check.check_bf_file_resolver_options(self._options)

  def resolve_gen(self, where):
    where = bf_check.check_file_or_dir_seq(object_util.listify(where))

    options = bf_file_finder_options()
    options.entry_class = bf_file_resolver_entry
    finder = bf_file_finder(options = options)
    for next_where in where:
      if path.isfile(next_where):
        entry = bf_file_resolver_entry(next_where)
        if finder._entry_matches(entry, next_where, {}):
          yield entry
      elif path.isdir(next_where):
        for entry in finder.find_gen(next_where):
          yield entry
    
  def resolve(self, where):
    result = bf_entry_list()
    for entry in self.resolve_gen(where):
      result.append(entry)
    return result

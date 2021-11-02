#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#import re
from collections import namedtuple

#from bes.common.algorithm import algorithm
from bes.common.check import check
#from bes.common.json_util import json_util
#from bes.common.string_util import string_util
#from bes.common.type_checked_list import type_checked_list
#from bes.data_output.data_output import data_output
#from bes.data_output.data_output_style import data_output_style
#from bes.data_output.data_output_options import data_output_options
#from bes.text.text_line_parser import text_line_parser
from bes.version.software_version import software_version

#from .git_commit_hash import git_commit_hash
#from .git_error import git_error
#from .git_tag_sort_type import git_tag_sort_type

class git_tag(namedtuple('git_tag', 'name, commit, commit_short, peeled')):

  def __new__(clazz, name, commit, commit_short, peeled):
    return clazz.__bases__[0].__new__(clazz, name, commit, commit_short, peeled)

  def to_dict(self):
    return dict(self._asdict())
  
check.register_class(git_tag, include_seq = False)

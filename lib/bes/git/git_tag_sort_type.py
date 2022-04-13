#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .git_error import git_error

class git_tag_sort_type(object):

  SORT_TYPES = ( 'lexical', 'version' )
  DEFAULT_SORT_TYPE = 'version'

  @classmethod
  def sort_type_is_valid(clazz, sort_type):
    check.check_string(sort_type)
    
    return sort_type in clazz.SORT_TYPES

  @classmethod
  def check_sort_type(clazz, sort_type):
    sort_type = sort_type or clazz.DEFAULT_SORT_TYPE
    if not clazz.sort_type_is_valid(sort_type):
      raise git_error('invalid sort_type: "{}".  Should be one of: {}'.format(sort_type,
                                                                              ' '.join(clazz.SORT_TYPES)))
    return sort_type

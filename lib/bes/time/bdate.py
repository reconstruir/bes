#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

from .btimezone import btimezone

class bdate(object):
  'Stuff to help dealing with dates'

  @classmethod
  def make_date_with_local_timezone(clazz, **kwargs):
    'Return the current local timezone.'

    return datetime(**kwargs, tzinfo = btimezone.local_timezone())

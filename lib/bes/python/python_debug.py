#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.debug.debug_timer import debug_timer

class python_debug(object):
  'Bes project.'

  timer = debug_timer('python_debug', disabled = False) #, level = 'error')

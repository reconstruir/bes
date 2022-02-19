#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import locale

class locale_override(object):

  def __init__(self, category, locale = None):
    self._category = category
    self._locale = locale
    self._original_category = None
    self._original_locale = None
    
  def __enter__(self):
    self._original_category, self._original_locale = locale.getlocale()
    locale.setlocale(self._category, self._locale)
  
  def __exit__(self, type, value, traceback):
    locale.setlocale(self._original_category, self._original_locale)

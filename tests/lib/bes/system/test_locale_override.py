#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import locale
from bes.testing.unit_test import unit_test
from bes.system.locale_override import locale_override

class test_locale_override(unit_test):

  def test_locale_override(self):
    original_locale = locale.getlocale()
    print(f'original_locale={original_locale}')
    with locale_override(locale.LC_ALL, 'en_US.UTF-8') as ctx:
      print(f'loc={locale.getlocale()}')
      self.assertEqual( 1234.5, locale.atof('1,234.5') )
    self.assertEqual( original_locale, locale.getlocale() )
  
if __name__ == '__main__':
  unit_test.main()

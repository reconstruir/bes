#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from datetime import timedelta

from bes.files.match.bf_file_matcher_item_timedelta import bf_file_matcher_item_timedelta
from bes.files.bf_entry import bf_entry
from bes.files.bf_date import bf_date
from bes.files.bf_file_ops import bf_file_ops

from bes.testing.unit_test import unit_test

class test_bf_file_matcher_item_timedelta(unit_test):

  # FIXME THIS IS COMPLETELY WRONG
  def xtest_match(self):
    tmp_dir = self.make_temp_dir()

    date_2022 = self._make_test_date('2022-01-01')
    kiwi_2022 = self._make_test_file(tmp_dir, 'kiwi_2022.txt', date_2022)

    date_2023 = self._make_test_date('2023-01-01')
    kiwi_2023 = self._make_test_file(tmp_dir, 'kiwi_2023.txt', date_2023)

    date_2024 = self._make_test_date('2024-01-01')
    kiwi_2024 = self._make_test_file(tmp_dir, 'kiwi_2024.txt', date_2024)
    
    self.assertEqual( True, self._match(date_2023, 'lt', kiwi_2022) )
    self.assertEqual( True, self._match(date_2023, 'le', kiwi_2022) )
    self.assertEqual( False, self._match(date_2023, 'gt', kiwi_2022) )
    self.assertEqual( False, self._match(date_2023, 'ge', kiwi_2022) )
    self.assertEqual( True, self._match(date_2022, 'eq', kiwi_2022) )

  def _make_test_file(self, tmp_dir, basename, date):
    filename = path.join(tmp_dir, basename)
    bf_file_ops.save_text(filename, basename, encoding = 'utf-8')
    bf_date.set_modification_date(filename, date)
    return filename

  @classmethod
  def _make_test_date(clazz, date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')

  def _match(self, date, comparison_type, filename, file_type = None):
    entry = bf_entry(filename)
    matcher = bf_file_matcher_item_datetime(date,
                                            comparison_type,
                                            file_type = file_type)
    return matcher.match(entry)
  
if __name__ == '__main__':
  unit_test.main()

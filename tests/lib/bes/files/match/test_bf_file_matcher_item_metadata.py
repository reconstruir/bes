#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.match.bf_file_matcher_item_metadata import bf_file_matcher_item_metadata
from bes.files.bf_entry import bf_entry
from bes.files.metadata.bf_metadata import bf_metadata

from bes.testing.unit_test import unit_test

from _bes_unit_test_common.files.metadata.example_metadata_fruits_factory import example_metadata_fruits_factory

class test_bf_file_matcher_item_metadata(unit_test):
  
  def test_match_one_metadata_any(self):
    tmp1 = self.make_temp_file(dir = __file__, content = b'1234')
    tmp2 = self.make_temp_file(dir = __file__, content = b'123456')

    self.assertEqual( True, self._match({ 'acme__fruit__kiwi__1.0': 4 }, tmp1) )
    self.assertEqual( False, self._match({ 'acme__fruit__kiwi__1.0': 4 }, tmp2) )

  def xtest_match_two_metadata_all(self):
    tmp1 = self.make_temp_file(dir = __file__, content = 'brie')
    tmp2 = self.make_temp_file(dir = __file__, content = 'manchego')

    bf_attr.set_int(tmp1, 'acme__fruit__kiwi__1.0', 666)
    bf_attr.set_string(tmp1, 'acme__fruit__name__1.0', 'fred')
    bf_attr.set_int(tmp2, 'acme__fruit__kiwi__1.0', 42)
    bf_attr.set_string(tmp2, 'acme__fruit__name__1.0', 'joe')

    self.assertEqual( True, self._match({
      'acme__fruit__kiwi__1.0': 666,
      'acme__fruit__name__1.0': 'fred',
    }, tmp1) )
    self.assertEqual( False, self._match({
      'acme__fruit__kiwi__1.0': 666,
      'acme__fruit__name__1.0': 'fred',
    }, tmp2) )

  def _match(self, metadata, filename):
    entry = bf_entry(filename)
    matcher = bf_file_matcher_item_metadata(metadata)
    return matcher.match(entry)
                                     
if __name__ == '__main__':
  unit_test.main()

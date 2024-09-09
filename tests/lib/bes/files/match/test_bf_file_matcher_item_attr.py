#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.match.bf_file_matcher_item_attr import bf_file_matcher_item_attr
from bes.files.match.bf_file_matcher_options import bf_file_matcher_options
from bes.files.bf_entry import bf_entry
from bes.files.attr.bf_attr import bf_attr

from bes.testing.unit_test import unit_test

from _bes_unit_test_common.files.attr.fruits_factory import fruits_factory

class test_bf_file_matcher_item_attr(unit_test):

  _attr = bf_attr()
  def test_match_one_attr_any(self):
    tmp1 = self.make_temp_file(dir = __file__, content = 'brie')
    tmp2 = self.make_temp_file(dir = __file__, content = 'manchego')

    self._attr.set_int(tmp1, 'acme/fruit/kiwi/1.0', 666)
    self._attr.set_int(tmp2, 'acme/fruit/kiwi/1.0', 42)

    self.assertEqual( True, self._match({ 'acme/fruit/kiwi/1.0': 666 }, tmp1, match_type = 'ANY') )
    self.assertEqual( False, self._match({ 'acme/fruit/kiwi/1.0': 666 }, tmp2, match_type = 'ANY') )

  def test_match_two_attr_all(self):
    tmp1 = self.make_temp_file(dir = __file__, content = 'brie')
    tmp2 = self.make_temp_file(dir = __file__, content = 'manchego')

    self._attr.set_int(tmp1, 'acme/fruit/kiwi/1.0', 666)
    self._attr.set_string(tmp1, 'acme/fruit/name/1.0', 'fred')
    self._attr.set_int(tmp2, 'acme/fruit/kiwi/1.0', 42)
    self._attr.set_string(tmp2, 'acme/fruit/name/1.0', 'joe')

    self.assertEqual( True, self._match({
      'acme/fruit/kiwi/1.0': 666,
      'acme/fruit/name/1.0': 'fred',
    }, tmp1, match_type = 'ALL') )
    self.assertEqual( False, self._match({
      'acme/fruit/kiwi/1.0': 666,
      'acme/fruit/name/1.0': 'fred',
    }, tmp2, match_type = 'ALL') )

  def _match(self, attrs, filename, **options_args):
    entry = bf_entry(filename)
    options = bf_file_matcher_options(**options_args)
    matcher = bf_file_matcher_item_attr(attrs)
    return matcher.match(entry, options)
                                     
if __name__ == '__main__':
  unit_test.main()

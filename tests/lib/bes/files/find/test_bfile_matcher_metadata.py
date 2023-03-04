#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.find.bfile_matcher_metadata import bfile_matcher_metadata
from bes.files.find.bfile_filename_matcher_options import bfile_filename_matcher_options
from bes.files.bfile_entry import bfile_entry
from bes.files.metadata.bfile_metadata import bfile_metadata

from bes.testing.unit_test import unit_test

from _bes_unit_test_common.files.metadata.example_metadata_fruits_factory import example_metadata_fruits_factory

class test_bfile_matcher_metadata(unit_test):
  
  def xtest_match_one_metadata_any(self):
    tmp1 = self.make_temp_file(dir = __file__, content = b'1234')
    tmp2 = self.make_temp_file(dir = __file__, content = b'123456')

#    bfile_attr.set_int(tmp1, 'acme/fruit/kiwi/1.0', 666)
#    bfile_attr.set_int(tmp2, 'acme/fruit/kiwi/1.0', 42)

    #self.assertEqual( 5.0, bfile_metadata.get_metadata(tmp, 'acme/fruit/cherry/2.0') )
    
    self.assertEquals( True, self._match({ 'acme/fruit/kiwi/1.0': 666 }, tmp1, match_type = 'ANY') )
    self.assertEquals( False, self._match({ 'acme/fruit/kiwi/1.0': 666 }, tmp2, match_type = 'ANY') )

  def xtest_match_two_metadata_all(self):
    tmp1 = self.make_temp_file(dir = __file__, content = 'brie')
    tmp2 = self.make_temp_file(dir = __file__, content = 'manchego')

    bfile_attr.set_int(tmp1, 'acme/fruit/kiwi/1.0', 666)
    bfile_attr.set_string(tmp1, 'acme/fruit/name/1.0', 'fred')
    bfile_attr.set_int(tmp2, 'acme/fruit/kiwi/1.0', 42)
    bfile_attr.set_string(tmp2, 'acme/fruit/name/1.0', 'joe')

    self.assertEquals( True, self._match({
      'acme/fruit/kiwi/1.0': 666,
      'acme/fruit/name/1.0': 'fred',
    }, tmp1, match_type = 'ALL') )
    self.assertEquals( False, self._match({
      'acme/fruit/kiwi/1.0': 666,
      'acme/fruit/name/1.0': 'fred',
    }, tmp2, match_type = 'ALL') )

  def _match(self, attrs, filename, **options_args):
    entry = bfile_entry(filename)
    options = bfile_filename_matcher_options(**options_args)
    matcher = bfile_matcher_attr(attrs, options)
    return matcher.match(entry)
                                     
if __name__ == '__main__':
  unit_test.main()

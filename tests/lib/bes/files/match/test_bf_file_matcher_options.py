#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.match.bf_file_matcher_options import bf_file_matcher_options
from bes.files.match.bf_file_matcher_type import bf_file_matcher_type
from bes.files.bf_path_type import bf_path_type

from bes.testing.unit_test import unit_test

class test_bf_file_matcher_options(unit_test):
  
  def test_do_dict(self):
    o = bf_file_matcher_options()
    self.assertEqual( {
      'ignore_case': False,
      'match_type': bf_file_matcher_type.ANY,
      'path_type': bf_path_type.RELATIVE,
    }, o.to_dict() )
    o.ignore_case = True
    self.assertEqual( {
      'ignore_case': True,
      'match_type': bf_file_matcher_type.ANY,
      'path_type': bf_path_type.RELATIVE,
    }, o.to_dict() )

  def test___setattr__match_type(self):
    o = bf_file_matcher_options()
    self.assertEqual( bf_file_matcher_type.ANY, o.match_type )

    o.match_type = bf_file_matcher_type.ALL
    self.assertEqual( bf_file_matcher_type.ALL, o.match_type )

    o.match_type = bf_file_matcher_type.NONE
    self.assertEqual( bf_file_matcher_type.NONE, o.match_type )

  def test___setattr__match_type_with_cast(self):
    o = bf_file_matcher_options()
    self.assertEqual( bf_file_matcher_type.ANY, o.match_type )

    o.match_type = 'ALL'
    self.assertEqual( bf_file_matcher_type.ALL, o.match_type )
    
if __name__ == '__main__':
  unit_test.main()

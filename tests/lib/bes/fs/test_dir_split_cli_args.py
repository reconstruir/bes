#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.program_unit_test import program_unit_test
from bes.fs.testing.temp_content import temp_content
from bes.fs.testing.temp_content import multiplied_temp_content

from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class test_dir_split_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '../../../../bin/best.py')

  def test_split_chunks_of_two(self):
    t = self._split_test([
      multiplied_temp_content('apple', 5),
      multiplied_temp_content('kiwi', 2),
      multiplied_temp_content('lemon', 3),
      multiplied_temp_content('blueberry', 1),
    ], 1, 2)
    expected = [
      'chunk-1',
      'chunk-1/apple1.txt',
      'chunk-1/apple2.txt',
      'chunk-2',
      'chunk-2/apple3.txt',
      'chunk-2/apple4.txt',
      'chunk-3',
      'chunk-3/apple5.txt',
      'chunk-3/blueberry1.txt',
      'chunk-4',
      'chunk-4/kiwi1.txt',
      'chunk-4/kiwi2.txt',
      'chunk-5',
      'chunk-5/lemon1.txt',
      'chunk-5/lemon2.txt',
      'chunk-6',
      'chunk-6/lemon3.txt',
    ]
    self.assertEqual( 0, t.result.exit_code )
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )
    
  def _split_test(self, multiplied_content_items, content_multiplier, chunk_size, extra_content_items = None):
    with dir_operation_tester(multiplied_content_items = multiplied_content_items,
                              content_multiplier = content_multiplier,
                              extra_content_items = extra_content_items) as test:
      args = [
        'dir_split',
        'split',
        '--prefix', 'chunk-',
        '--dst-dir', test.dst_dir,
        '--chunk-size', str(chunk_size),
        test.src_dir,
      ]
      test.result = self.run_program(self._program, args)
    return test

if __name__ == '__main__':
  program_unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.program_unit_test import program_unit_test
from bes.fs.testing.temp_content import temp_content
from bes.fs.file_split_options import file_split_options

from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

_DEFAULT_FILE_SPLIT_OPTIONS = file_split_options()

class test_file_split_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '../../../../bin/best.py')

  def test_find_and_unsplit(self):
    items = [
      temp_content('file', 'src/a/foo/kiwi.txt', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/parts/xfoo.txt.001', 'garbage', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.001', 'foo001', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.002', 'foo002', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.003', 'foo003', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.xx4', 'garbage', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.003.garbage', 'garbage', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.01', 'lemon01', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.02', 'lemon02', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.03', 'lemon03', 0o0644),
    ]
    t = self._find_and_unsplit_test(extra_content_items = items,
                           recursive = True)
    self.assertEqual( [
      'a',
      'a/foo',
      'a/foo/kiwi.txt',
      'a/parts',
      'a/parts/foo.txt',
      'a/parts/foo.txt.003.garbage',
      'a/parts/foo.txt.xx4',
      'a/parts/xfoo.txt.001',
      'b',
      'b/icons',
      'b/icons/lemon.jpg',
    ], t.src_files )
    self.assert_text_file_equal( 'foo001foo002foo003', f'{t.src_dir}/a/parts/foo.txt' )
    self.assert_text_file_equal( 'lemon01lemon02lemon03', f'{t.src_dir}/b/icons/lemon.jpg' )

  def _find_and_unsplit_test(self,
                             extra_content_items = None,
                             recursive = False,
                             check_downloading = _DEFAULT_FILE_SPLIT_OPTIONS.check_downloading,
                             check_modified = _DEFAULT_FILE_SPLIT_OPTIONS.check_modified,
                             check_modified_interval = _DEFAULT_FILE_SPLIT_OPTIONS.check_modified_interval):
    options = file_split_options(recursive = recursive,
                                 check_downloading = check_downloading)
    with dir_operation_tester(extra_content_items = extra_content_items) as test:
      args = [
        'file_split',
        'unsplit',
        test.src_dir,
      ]
      if recursive:
        args.append('--recursive')
      if check_downloading:
        args.append('--check-downloading')
      test.result = self.run_program(self._program, args)
    return test

if __name__ == '__main__':
  program_unit_test.main()

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.program_unit_test import program_unit_test
from bes.fs.testing.temp_content import temp_content
from bes.fs.testing.temp_content import multiplied_temp_content

from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class test_dirs_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '../../../../bin/best.py')

  def test_remove_empty(self):
    t = self._test([
      'dir  src/empty1             ""              700',
      'file src/readme.md          "readme.md"     644',
      'file src/a/kiwi-30.jpg      "kiwi-30.txt"   644',
      'dir  src/a/empty2           ""              700',
      'file src/b/lemon-10.jpg     "lemon-10.txt"  644',
      'file src/c/cheese-10.jpg    "cheese-10.jpg" 644',
      'file src/icons/foo.png      "foo.png"       644',
      'file src/lemon-40.jpg       "lemon-40.txt"  644',
      'dir  src/a/empty2           ""              700',
      'dir  src/foo/bar/baz/empty3 "lemon-40.txt"  700',
    ], recursive = False)
    expected = [
      'a',
      'a/empty2',
      'b',
      'c',
      'foo',
      'foo/bar',
      'foo/bar/baz',
      'foo/bar/baz/empty3',
      'icons',
    ]
    self.assertEqual( 0, t.result.exit_code )
    self.assert_filename_list_equal( expected, t.src_dirs )

  def test_remove_empty_recursive(self):
    t = self._test([
      'dir  src/empty1             ""              700',
      'file src/readme.md          "readme.md"     644',
      'file src/a/kiwi-30.jpg      "kiwi-30.txt"   644',
      'dir  src/a/empty2           ""              700',
      'file src/b/lemon-10.jpg     "lemon-10.txt"  644',
      'file src/c/cheese-10.jpg    "cheese-10.jpg" 644',
      'file src/icons/foo.png      "foo.png"       644',
      'file src/lemon-40.jpg       "lemon-40.txt"  644',
      'dir  src/a/empty2           ""              700',
      'dir  src/foo/bar/baz/empty3 "lemon-40.txt"  700',
    ], recursive = True)
    expected = [
      'a',
      'b',
      'c',
      'icons',
    ]
    self.assertEqual( 0, t.result.exit_code )
    self.assert_filename_list_equal( expected, t.src_dirs )

  def test_remove_empty_dry_run(self):
    t = self._test([
      'dir  src/empty1             ""              700',
      'file src/readme.md          "readme.md"     644',
      'file src/a/kiwi-30.jpg      "kiwi-30.txt"   644',
      'dir  src/a/empty2           ""              700',
      'file src/b/lemon-10.jpg     "lemon-10.txt"  644',
      'file src/c/cheese-10.jpg    "cheese-10.jpg" 644',
      'file src/icons/foo.png      "foo.png"       644',
      'file src/lemon-40.jpg       "lemon-40.txt"  644',
      'dir  src/a/empty2           ""              700',
      'dir  src/foo/bar/baz/empty3 "lemon-40.txt"  700',
    ], recursive = True, dry_run = True)
    expected = [
      'a',
      'a/empty2',
      'b',
      'c',
      'empty1',
      'foo',
      'foo/bar',
      'foo/bar/baz',
      'foo/bar/baz/empty3',
      'icons',
    ]
    self.assertEqual( 0, t.result.exit_code )
    self.assert_filename_list_equal( expected, t.src_dirs )
    self.assert_string_equal_fuzzy( f'''
DRY_RUN: would remove {t.src_dir}/a/empty2
DRY_RUN: would remove {t.src_dir}/empty1
DRY_RUN: would remove {t.src_dir}/foo/bar/baz/empty3
''', t.result.output )
    
  def _test(self, items, recursive = False, dry_run = False):
    with dir_operation_tester(extra_content_items = items) as test:
      args = [
        'dirs',
        'remove_empty',
        test.src_dir,
      ]
      if recursive:
        args.append('--recursive')
      if dry_run:
        args.append('--dry-run')
      test.result = self.run_program(self._program, args)
    return test

if __name__ == '__main__':
  program_unit_test.main()

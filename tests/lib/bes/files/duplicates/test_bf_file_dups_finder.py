#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from os import path
from datetime import datetime
from datetime import timedelta
from bes.files.bf_path import bf_path
from bes.files.duplicates.bf_file_dups_finder import bf_file_dups_finder
from bes.files.duplicates.bf_file_dups_finder_options import bf_file_dups_finder_options
from bes.files.duplicates.bf_file_dups_entry_list import bf_file_dups_entry_list
from bes.files.hashing.bf_hasher_hashlib import bf_hasher_hashlib
from bes.fs.testing.temp_content import temp_content
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class test_file_duplicates(unit_test):

  def test__resolve_files(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
    ]
    with dir_operation_tester(extra_content_items = items) as tester:
      hasher = bf_hasher_hashlib()
      finder = bf_file_dups_finder(hasher = hasher)
      resolved_files = finder._resolve_files(tester.src_dir)
      self.assert_json_equal( '''
[
  {
    "filename": "a/apple.jpg",
    "root_dir": "${root_dir}",
    "index": 0,
    "found_index": 0
  },
  {
    "filename": "a/kiwi.jpg",
    "root_dir": "${root_dir}",
    "index": 1,
    "found_index": 1
  },
  {
    "filename": "a/lemon.jpg",
    "root_dir": "${root_dir}",
    "index": 2,
    "found_index": 2
  },
  {
    "filename": "b/kiwi_dup1.jpg",
    "root_dir": "${root_dir}",
    "index": 3,
    "found_index": 3
  },
  {
    "filename": "c/kiwi_dup2.jpg",
    "root_dir": "${root_dir}",
    "index": 4,
    "found_index": 4
  }
]
''', resolved_files.to_json().replace(tester.src_dir, '${root_dir}') )

  def test_find_duplicates_basic(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/d/empty1.txt', '', 0o0644),
      temp_content('file', 'src/e/empty2.txt', '', 0o0644),
      temp_content('resource_fork', 'src/e/._empty2.txt', '', 0o0644),
    ]
    with dir_operation_tester(extra_content_items = items) as tester:
      hasher = bf_hasher_hashlib()
      finder = bf_file_dups_finder(hasher = hasher)
      result = finder.find_duplicates([ tester.src_dir ])
      print(f'\n')
      print(f'CACA0: {type(result)}')
      print(f'CACA1: {type(result.resolved_entries)}')
      print(f'CACA2: {type(result.resolved_entries[0])}')
      #self.assertEqual( True, isinstance(result.resolved_entries, bf_entry_list) )
      
      self.assert_json_equal( '''
{
  "resolved_entries": {
    "_values": [
      {
        "_filename": "a/apple.jpg",
        "_root_dir": "${root_dir}",
        "_index": 0,
        "_found_index": 0,
        "filename": "${root_dir}/a/apple.jpg",
        "relative_filename": "a/apple.jpg",
        "absolute_filename": "${root_dir}/a/apple.jpg"
      },
      {
        "_filename": "a/kiwi.jpg",
        "_root_dir": "${root_dir}",
        "_index": 1,
        "_found_index": 1,
        "filename": "${root_dir}/a/kiwi.jpg",
        "relative_filename": "a/kiwi.jpg",
        "absolute_filename": "${root_dir}/a/kiwi.jpg"
      },
      {
        "_filename": "a/lemon.jpg",
        "_root_dir": "${root_dir}",
        "_index": 2,
        "_found_index": 2,
        "filename": "${root_dir}/a/lemon.jpg",
        "relative_filename": "a/lemon.jpg",
        "absolute_filename": "${root_dir}/a/lemon.jpg"
      },
      {
        "_filename": "b/kiwi_dup1.jpg",
        "_root_dir": "${root_dir}",
        "_index": 3,
        "_found_index": 3,
        "filename": "${root_dir}/b/kiwi_dup1.jpg",
        "relative_filename": "b/kiwi_dup1.jpg",
        "absolute_filename": "${root_dir}/b/kiwi_dup1.jpg"
      },
      {
        "_filename": "c/kiwi_dup2.jpg",
        "_root_dir": "${root_dir}",
        "_index": 4,
        "_found_index": 4,
        "filename": "${root_dir}/c/kiwi_dup2.jpg",
        "relative_filename": "c/kiwi_dup2.jpg",
        "absolute_filename": "${root_dir}/c/kiwi_dup2.jpg"
      },
      {
        "_filename": "d/empty1.txt",
        "_root_dir": "${root_dir}",
        "_index": 5,
        "_found_index": 5,
        "filename": "${root_dir}/d/empty1.txt",
        "relative_filename": "d/empty1.txt",
        "absolute_filename": "${root_dir}/d/empty1.txt"
      },
      {
        "_filename": "e/empty2.txt",
        "_root_dir": "${root_dir}",
        "_index": 6,
        "_found_index": 6,
        "filename": "${root_dir}/e/empty2.txt",
        "relative_filename": "e/empty2.txt",
        "absolute_filename": "${root_dir}/e/empty2.txt"
      }
    ]
  },
  "duplicate_items": {
    "_values": [
      {
        "entry": {
          "_filename": "a/kiwi.jpg",
          "_root_dir": "${root_dir}",
          "_index": 1,
          "_found_index": 1,
          "filename": "${root_dir}/a/kiwi.jpg",
          "relative_filename": "a/kiwi.jpg",
          "absolute_filename": "${root_dir}/a/kiwi.jpg"
        },
        "duplicates": {
          "_values": [
            {
              "_filename": "b/kiwi_dup1.jpg",
              "_root_dir": "${root_dir}",
              "_index": 3,
              "_found_index": 3,
              "filename": "${root_dir}/b/kiwi_dup1.jpg",
              "relative_filename": "b/kiwi_dup1.jpg",
              "absolute_filename": "${root_dir}/b/kiwi_dup1.jpg"
            },
            {
              "_filename": "c/kiwi_dup2.jpg",
              "_root_dir": "${root_dir}",
              "_index": 4,
              "_found_index": 4,
              "filename": "${root_dir}/c/kiwi_dup2.jpg",
              "relative_filename": "c/kiwi_dup2.jpg",
              "absolute_filename": "${root_dir}/c/kiwi_dup2.jpg"
            }
          ]
        }
      }
    ]
  }
}
''', result.to_json().replace(tester.src_dir, '${root_dir}') )

  def test_find_duplicates_with_empty_files(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/d/empty1.txt', '', 0o0644),
      temp_content('file', 'src/e/empty2.txt', '', 0o0644),
    ]
    with dir_operation_tester(extra_content_items = items) as tester:
      hasher = bf_hasher_hashlib()
      options = bf_file_dups_finder_options(include_empty_files = True)
      finder = bf_file_dups_finder(hasher = hasher, options = options)
      result = finder.find_duplicates([ tester.src_dir ])
      self.assert_json_equal( '''
{
  "resolved_entries": {
    "_values": [
      {
        "_filename": "a/apple.jpg",
        "_root_dir": "${root_dir}",
        "_index": 0,
        "_found_index": 0,
        "filename": "${root_dir}/a/apple.jpg",
        "relative_filename": "a/apple.jpg",
        "absolute_filename": "${root_dir}/a/apple.jpg"
      },
      {
        "_filename": "a/kiwi.jpg",
        "_root_dir": "${root_dir}",
        "_index": 1,
        "_found_index": 1,
        "filename": "${root_dir}/a/kiwi.jpg",
        "relative_filename": "a/kiwi.jpg",
        "absolute_filename": "${root_dir}/a/kiwi.jpg"
      },
      {
        "_filename": "a/lemon.jpg",
        "_root_dir": "${root_dir}",
        "_index": 2,
        "_found_index": 2,
        "filename": "${root_dir}/a/lemon.jpg",
        "relative_filename": "a/lemon.jpg",
        "absolute_filename": "${root_dir}/a/lemon.jpg"
      },
      {
        "_filename": "b/kiwi_dup1.jpg",
        "_root_dir": "${root_dir}",
        "_index": 3,
        "_found_index": 3,
        "filename": "${root_dir}/b/kiwi_dup1.jpg",
        "relative_filename": "b/kiwi_dup1.jpg",
        "absolute_filename": "${root_dir}/b/kiwi_dup1.jpg"
      },
      {
        "_filename": "c/kiwi_dup2.jpg",
        "_root_dir": "${root_dir}",
        "_index": 4,
        "_found_index": 4,
        "filename": "${root_dir}/c/kiwi_dup2.jpg",
        "relative_filename": "c/kiwi_dup2.jpg",
        "absolute_filename": "${root_dir}/c/kiwi_dup2.jpg"
      },
      {
        "_filename": "d/empty1.txt",
        "_root_dir": "${root_dir}",
        "_index": 5,
        "_found_index": 5,
        "filename": "${root_dir}/d/empty1.txt",
        "relative_filename": "d/empty1.txt",
        "absolute_filename": "${root_dir}/d/empty1.txt"
      },
      {
        "_filename": "e/empty2.txt",
        "_root_dir": "${root_dir}",
        "_index": 6,
        "_found_index": 6,
        "filename": "${root_dir}/e/empty2.txt",
        "relative_filename": "e/empty2.txt",
        "absolute_filename": "${root_dir}/e/empty2.txt"
      }
    ]
  },
  "duplicate_items": {
    "_values": [
      {
        "entry": {
          "_filename": "a/kiwi.jpg",
          "_root_dir": "${root_dir}",
          "_index": 1,
          "_found_index": 1,
          "filename": "${root_dir}/a/kiwi.jpg",
          "relative_filename": "a/kiwi.jpg",
          "absolute_filename": "${root_dir}/a/kiwi.jpg"
        },
        "duplicates": {
          "_values": [
            {
              "_filename": "b/kiwi_dup1.jpg",
              "_root_dir": "${root_dir}",
              "_index": 3,
              "_found_index": 3,
              "filename": "${root_dir}/b/kiwi_dup1.jpg",
              "relative_filename": "b/kiwi_dup1.jpg",
              "absolute_filename": "${root_dir}/b/kiwi_dup1.jpg"
            },
            {
              "_filename": "c/kiwi_dup2.jpg",
              "_root_dir": "${root_dir}",
              "_index": 4,
              "_found_index": 4,
              "filename": "${root_dir}/c/kiwi_dup2.jpg",
              "relative_filename": "c/kiwi_dup2.jpg",
              "absolute_filename": "${root_dir}/c/kiwi_dup2.jpg"
            }
          ]
        }
      },
      {
        "entry": {
          "_filename": "d/empty1.txt",
          "_root_dir": "${root_dir}",
          "_index": 5,
          "_found_index": 5,
          "filename": "${root_dir}/d/empty1.txt",
          "relative_filename": "d/empty1.txt",
          "absolute_filename": "${root_dir}/d/empty1.txt"
        },
        "duplicates": {
          "_values": [
            {
              "_filename": "e/empty2.txt",
              "_root_dir": "${root_dir}",
              "_index": 6,
              "_found_index": 6,
              "filename": "${root_dir}/e/empty2.txt",
              "relative_filename": "e/empty2.txt",
              "absolute_filename": "${root_dir}/e/empty2.txt"
            }
          ]
        }
      }
    ]
  }
}
''', result.to_json().replace(tester.src_dir, '${root_dir}') )

  def test_find_duplicates_with_resource_forks(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/d/empty1.txt', '', 0o0644),
      temp_content('resource_fork', 'src/d/._empty1.txt', '', 0o0644),
      temp_content('file', 'src/e/empty2.txt', '', 0o0644),
      temp_content('resource_fork', 'src/e/._empty2.txt', '', 0o0644),
    ]
    with dir_operation_tester(extra_content_items = items) as tester:
      hasher = bf_hasher_hashlib()
      options = bf_file_dups_finder_options(include_resource_forks = True)
      finder = bf_file_dups_finder(hasher = hasher, options = options)
      result = finder.find_duplicates([ tester.src_dir ])
      self.assert_json_equal( '''
{
  "resolved_entries": {
    "_values": [
      {
        "_filename": "a/apple.jpg",
        "_root_dir": "${root_dir}",
        "_index": 0,
        "_found_index": 0,
        "filename": "${root_dir}/a/apple.jpg",
        "relative_filename": "a/apple.jpg",
        "absolute_filename": "${root_dir}/a/apple.jpg"
      },
      {
        "_filename": "a/kiwi.jpg",
        "_root_dir": "${root_dir}",
        "_index": 1,
        "_found_index": 1,
        "filename": "${root_dir}/a/kiwi.jpg",
        "relative_filename": "a/kiwi.jpg",
        "absolute_filename": "${root_dir}/a/kiwi.jpg"
      },
      {
        "_filename": "a/lemon.jpg",
        "_root_dir": "${root_dir}",
        "_index": 2,
        "_found_index": 2,
        "filename": "${root_dir}/a/lemon.jpg",
        "relative_filename": "a/lemon.jpg",
        "absolute_filename": "${root_dir}/a/lemon.jpg"
      },
      {
        "_filename": "b/kiwi_dup1.jpg",
        "_root_dir": "${root_dir}",
        "_index": 3,
        "_found_index": 3,
        "filename": "${root_dir}/b/kiwi_dup1.jpg",
        "relative_filename": "b/kiwi_dup1.jpg",
        "absolute_filename": "${root_dir}/b/kiwi_dup1.jpg"
      },
      {
        "_filename": "c/kiwi_dup2.jpg",
        "_root_dir": "${root_dir}",
        "_index": 4,
        "_found_index": 4,
        "filename": "${root_dir}/c/kiwi_dup2.jpg",
        "relative_filename": "c/kiwi_dup2.jpg",
        "absolute_filename": "${root_dir}/c/kiwi_dup2.jpg"
      },
      {
        "_filename": "d/._empty1.txt",
        "_root_dir": "${root_dir}",
        "_index": 5,
        "_found_index": 5,
        "filename": "${root_dir}/d/._empty1.txt",
        "relative_filename": "d/._empty1.txt",
        "absolute_filename": "${root_dir}/d/._empty1.txt"
      },
      {
        "_filename": "d/empty1.txt",
        "_root_dir": "${root_dir}",
        "_index": 6,
        "_found_index": 6,
        "filename": "${root_dir}/d/empty1.txt",
        "relative_filename": "d/empty1.txt",
        "absolute_filename": "${root_dir}/d/empty1.txt"
      },
      {
        "_filename": "e/._empty2.txt",
        "_root_dir": "${root_dir}",
        "_index": 7,
        "_found_index": 7,
        "filename": "${root_dir}/e/._empty2.txt",
        "relative_filename": "e/._empty2.txt",
        "absolute_filename": "${root_dir}/e/._empty2.txt"
      },
      {
        "_filename": "e/empty2.txt",
        "_root_dir": "${root_dir}",
        "_index": 8,
        "_found_index": 8,
        "filename": "${root_dir}/e/empty2.txt",
        "relative_filename": "e/empty2.txt",
        "absolute_filename": "${root_dir}/e/empty2.txt"
      }
    ]
  },
  "duplicate_items": {
    "_values": [
      {
        "entry": {
          "_filename": "a/kiwi.jpg",
          "_root_dir": "${root_dir}",
          "_index": 1,
          "_found_index": 1,
          "filename": "${root_dir}/a/kiwi.jpg",
          "relative_filename": "a/kiwi.jpg",
          "absolute_filename": "${root_dir}/a/kiwi.jpg"
        },
        "duplicates": {
          "_values": [
            {
              "_filename": "b/kiwi_dup1.jpg",
              "_root_dir": "${root_dir}",
              "_index": 3,
              "_found_index": 3,
              "filename": "${root_dir}/b/kiwi_dup1.jpg",
              "relative_filename": "b/kiwi_dup1.jpg",
              "absolute_filename": "${root_dir}/b/kiwi_dup1.jpg"
            },
            {
              "_filename": "c/kiwi_dup2.jpg",
              "_root_dir": "${root_dir}",
              "_index": 4,
              "_found_index": 4,
              "filename": "${root_dir}/c/kiwi_dup2.jpg",
              "relative_filename": "c/kiwi_dup2.jpg",
              "absolute_filename": "${root_dir}/c/kiwi_dup2.jpg"
            }
          ]
        }
      },
      {
        "entry": {
          "_filename": "d/._empty1.txt",
          "_root_dir": "${root_dir}",
          "_index": 5,
          "_found_index": 5,
          "filename": "${root_dir}/d/._empty1.txt",
          "relative_filename": "d/._empty1.txt",
          "absolute_filename": "${root_dir}/d/._empty1.txt"
        },
        "duplicates": {
          "_values": [
            {
              "_filename": "e/._empty2.txt",
              "_root_dir": "${root_dir}",
              "_index": 7,
              "_found_index": 7,
              "filename": "${root_dir}/e/._empty2.txt",
              "relative_filename": "e/._empty2.txt",
              "absolute_filename": "${root_dir}/e/._empty2.txt"
            }
          ]
        }
      }
    ]
  }
}
''', result.to_json().replace(tester.src_dir, '${root_dir}') )

  def xtest_find_duplicates_with_ignore_filename(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/d/empty1.txt', '', 0o0644),
      temp_content('resource_fork', 'src/d/._empty1.txt', '', 0o0644),
      temp_content('file', 'src/e/empty2.txt', '', 0o0644),
      temp_content('resource_fork', 'src/e/._empty2.txt', '', 0o0644),
    ]
    with dir_operation_tester(extra_content_items = items) as tester:
      hasher = bf_hasher_hashlib()
      options = bf_file_dups_finder_options(ignore_filename = '.testing_test_ignore')
#      options = None
      finder = bf_file_dups_finder(hasher = hasher, options = options)
      result = finder.find_duplicates([ tester.src_dir ])
      print(f'CACA0: {type(result)}')
      print(f'CACA1: {type(result.resolved_entries)}')
      print(f'CACA2: {type(result.resolved_entries[0])}')
      self.assert_json_equal( '''
{
  "resolved_entries": {
    "_values": [
      {
        "_filename": "a/apple.jpg",
        "_root_dir": "${root_dir}",
        "_index": 0,
        "_found_index": 0,
        "filename": "${root_dir}/a/apple.jpg",
        "relative_filename": "a/apple.jpg",
        "absolute_filename": "${root_dir}/a/apple.jpg"
      },
      {
        "_filename": "a/kiwi.jpg",
        "_root_dir": "${root_dir}",
        "_index": 1,
        "_found_index": 1,
        "filename": "${root_dir}/a/kiwi.jpg",
        "relative_filename": "a/kiwi.jpg",
        "absolute_filename": "${root_dir}/a/kiwi.jpg"
      },
      {
        "_filename": "a/lemon.jpg",
        "_root_dir": "${root_dir}",
        "_index": 2,
        "_found_index": 2,
        "filename": "${root_dir}/a/lemon.jpg",
        "relative_filename": "a/lemon.jpg",
        "absolute_filename": "${root_dir}/a/lemon.jpg"
      },
      {
        "_filename": "b/kiwi_dup1.jpg",
        "_root_dir": "${root_dir}",
        "_index": 3,
        "_found_index": 3,
        "filename": "${root_dir}/b/kiwi_dup1.jpg",
        "relative_filename": "b/kiwi_dup1.jpg",
        "absolute_filename": "${root_dir}/b/kiwi_dup1.jpg"
      },
      {
        "_filename": "c/kiwi_dup2.jpg",
        "_root_dir": "${root_dir}",
        "_index": 4,
        "_found_index": 4,
        "filename": "${root_dir}/c/kiwi_dup2.jpg",
        "relative_filename": "c/kiwi_dup2.jpg",
        "absolute_filename": "${root_dir}/c/kiwi_dup2.jpg"
      },
      {
        "_filename": "d/empty1.txt",
        "_root_dir": "${root_dir}",
        "_index": 5,
        "_found_index": 5,
        "filename": "${root_dir}/d/empty1.txt",
        "relative_filename": "d/empty1.txt",
        "absolute_filename": "${root_dir}/d/empty1.txt"
      },
      {
        "_filename": "e/empty2.txt",
        "_root_dir": "${root_dir}",
        "_index": 6,
        "_found_index": 6,
        "filename": "${root_dir}/e/empty2.txt",
        "relative_filename": "e/empty2.txt",
        "absolute_filename": "${root_dir}/e/empty2.txt"
      }
    ]
  },
  "duplicate_items": {
    "_values": [
      {
        "entry": {
          "_filename": "a/kiwi.jpg",
          "_root_dir": "${root_dir}",
          "_index": 1,
          "_found_index": 1,
          "filename": "${root_dir}/a/kiwi.jpg",
          "relative_filename": "a/kiwi.jpg",
          "absolute_filename": "${root_dir}/a/kiwi.jpg"
        },
        "duplicates": {
          "_values": [
            {
              "_filename": "b/kiwi_dup1.jpg",
              "_root_dir": "${root_dir}",
              "_index": 3,
              "_found_index": 3,
              "filename": "${root_dir}/b/kiwi_dup1.jpg",
              "relative_filename": "b/kiwi_dup1.jpg",
              "absolute_filename": "${root_dir}/b/kiwi_dup1.jpg"
            },
            {
              "_filename": "c/kiwi_dup2.jpg",
              "_root_dir": "${root_dir}",
              "_index": 4,
              "_found_index": 4,
              "filename": "${root_dir}/c/kiwi_dup2.jpg",
              "relative_filename": "c/kiwi_dup2.jpg",
              "absolute_filename": "${root_dir}/c/kiwi_dup2.jpg"
            }
          ]
        }
      }
    ]
  }
}
''', result.to_json().replace(tester.src_dir, '${root_dir}') )
      
  def xtest_find_duplicates_basic(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
    ]
    t = self._call_find_duplicates(extra_content_items = items,
                                   recursive = True)
    self.assertEqual( self._xp_result_item_list([
      ( f'{t.src_dir}/a/kiwi.jpg', [
        f'{t.src_dir}/b/kiwi_dup1.jpg',
        f'{t.src_dir}/c/kiwi_dup2.jpg',
      ] ),
    ]), t.result.items )

  def xtest_find_duplicates_with_small_checksum_size(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
    ]
    t = self._call_find_duplicates(extra_content_items = items,
                                   recursive = True,
                                   small_checksum_size = 4)
    self.assertEqual( self._xp_result_item_list([
      ( f'{t.src_dir}/a/kiwi.jpg', [
        f'{t.src_dir}/b/kiwi_dup1.jpg',
        f'{t.src_dir}/c/kiwi_dup2.jpg',
      ] ),
    ]), t.result.items )

  def xtest_find_duplicates_correct_order(self):
    items = [
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/z/kiwi.jpg', 'this is kiwi', 0o0644),
    ]
    t = self._call_find_duplicates(extra_content_items = items,
                                   recursive = True)
    self.assertEqual( self._xp_result_item_list([
      ( f'{t.src_dir}/b/kiwi_dup1.jpg', [
        f'{t.src_dir}/c/kiwi_dup2.jpg',
        f'{t.src_dir}/z/kiwi.jpg',
      ] ),
    ]), t.result.items )

  def xtest_find_duplicates_with_prefer_prefixes(self):
    items = [
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/z/kiwi.jpg', 'this is kiwi', 0o0644),
    ]
    t = self._call_find_duplicates(extra_content_items = items,
                                   recursive = True,
                                   prefer_prefixes = [
                                     "f'{test.src_dir}/z'",
                                   ])
    self.assertEqual( self._xp_result_item_list([
      ( f'{t.src_dir}/z/kiwi.jpg', [
        f'{t.src_dir}/b/kiwi_dup1.jpg',
        f'{t.src_dir}/c/kiwi_dup2.jpg',
      ] ),
    ]), t.result.items )

  def xtest_find_duplicates_with_sort_key(self):
    items = [
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/z/kiwi.jpg', 'this is kiwi', 0o0644),
    ]
    sort_key = lambda filename: 0 if 'z' in bf_path.split(filename) else 1
    t = self._call_find_duplicates(extra_content_items = items,
                                   recursive = True,
                                   sort_key = sort_key)
    self.assertEqual( self._xp_result_item_list([
      ( f'{t.src_dir}/z/kiwi.jpg', [
        f'{t.src_dir}/b/kiwi_dup1.jpg',
        f'{t.src_dir}/c/kiwi_dup2.jpg',
      ] ),
    ]), t.result.items )

  def xtest_find_duplicates_with_sort_key_basename_length(self):
    items = [
      temp_content('file', 'src/a/kiwi_12345.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_1234.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_123.jpg', 'this is kiwi', 0o0644),
    ]
    t = self._call_find_duplicates(extra_content_items = items,
                                   recursive = True,
                                   sort_key = bf_file_dups_finder_options.sort_key_basename_length)
    self.assertEqual( self._xp_result_item_list([
      ( f'{t.src_dir}/c/kiwi_123.jpg', [
        f'{t.src_dir}/b/kiwi_1234.jpg',
        f'{t.src_dir}/a/kiwi_12345.jpg',
      ] ),
    ]), t.result.items )

  def xtest_find_duplicates_with_sort_key_modification_date(self):
    items = [
      temp_content('file', 'src/a/kiwi_03.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/b/kiwi_02.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_01.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
    ]
    def _ptf(test):
      file_util.set_modification_date(f'{test.src_dir}/c/kiwi_01.jpg',
                                      datetime.now())
      file_util.set_modification_date(f'{test.src_dir}/b/kiwi_02.jpg',
                                      datetime.now() - timedelta(days = 1))
      file_util.set_modification_date(f'{test.src_dir}/a/kiwi_03.jpg',
                                      datetime.now() - timedelta(days = 2))
    t = self._call_find_duplicates(extra_content_items = items,
                                   recursive = True,
                                   sort_key = bf_file_dups_finder_options.sort_key_modification_date,
                                   pre_test_function = _ptf)
    self.assertEqual( self._xp_result_item_list([
      ( f'{t.src_dir}/a/kiwi_03.jpg', [
        f'{t.src_dir}/b/kiwi_02.jpg',
        f'{t.src_dir}/c/kiwi_01.jpg',
      ] ),
    ]), t.result.items )

  def xtest_find_duplicates_with_ignore_files(self):
    ignore_file = self.make_temp_file(content = r'''
*.foo
''')
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/d/ignore.foo', 'this is kiwi', 0o0644),
    ]
    t = self._call_find_duplicates(extra_content_items = items,
                                   recursive = True,
                                   ignore_files = [ ignore_file ])
    self.assertEqual( self._xp_result_item_list([
      ( f'{t.src_dir}/a/kiwi.jpg', [
        f'{t.src_dir}/b/kiwi_dup1.jpg',
        f'{t.src_dir}/c/kiwi_dup2.jpg',
      ] ),
    ]), t.result.items )
    
  # FIXME: this test would prove the dups thing works
  # even with no write permissions for files
  @unit_test_function_skip.skip_if_not_unix()
  def xtest_find_duplicates_no_write_permission(self):
    if host.is_linux():
      shell = 'dash'
    else:
      shell = 'sh'
      
    sh_exe = which.which(shell)
    bin_dir = path.dirname(sh_exe)
    tmp_dir = self.make_temp_dir()
    sh_exe_dup = path.join(tmp_dir, 'dupsh.exe')
    file_util.copy(sh_exe, sh_exe_dup)
    result = self._test([ 
    ], [], extra_dirs_before = [
      _file_duplicate_tester_object._extra_dir(bin_dir, '${_bin}'),
      _file_duplicate_tester_object._extra_dir(tmp_dir, '${_tmp}'),
    ] )
    self.assertTrue( file_duplicates._dup_item('${{_bin}}/{}'.format(shell), [ '${_tmp}/dupsh.exe']) in result )

  def xtest_find_duplicates_with_empty_files(self):
    items = [
      temp_content('file', 'src/a/empty.jpg', '', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/empty_dup1.jpg', '', 0o0644),
      temp_content('file', 'src/c/empty_dup2.jpg', '', 0o0644),
    ]
    t = self._call_find_duplicates(extra_content_items = items,
                                   recursive = True,
                                   include_empty_files = True)
    self.assertEqual( self._xp_result_item_list([
      ( f'{t.src_dir}/a/empty.jpg', [
        f'{t.src_dir}/b/empty_dup1.jpg',
        f'{t.src_dir}/c/empty_dup2.jpg',
      ] ),
    ]), t.result.items )

  def xtest_find_duplicates_without_empty_files(self):
    items = [
      temp_content('file', 'src/a/empty.jpg', '', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/empty_dup1.jpg', '', 0o0644),
      temp_content('file', 'src/c/empty_dup2.jpg', '', 0o0644),
    ]
    t = self._call_find_duplicates(extra_content_items = items,
                                   recursive = True,
                                   include_empty_files = False)
    self.assertEqual( self._xp_result_item_list([]), t.result.items )

  def xtest_find_duplicates_with_setup(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
    ]
    options = bf_file_dups_finder_options(recursive = True)
    with dir_operation_tester(extra_content_items = items) as t:
      setup = file_duplicates.setup([ t.src_dir ], options = options)
      t.result = file_duplicates.find_duplicates_with_setup(setup)
      
    self.assertEqual( self._xp_result_item_list([
      ( f'{t.src_dir}/a/kiwi.jpg', [
        f'{t.src_dir}/b/kiwi_dup1.jpg',
        f'{t.src_dir}/c/kiwi_dup2.jpg',
      ] ),
    ]), t.result.items )

  def xtest_find_file_duplicates(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'foo/cheese/brie.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'foo/cheese/cheddar.jpg', 'this is cheddar', 0o0644),
    ]
    t = self._call_find_file_duplicates('foo/cheese/brie.jpg',
                                        extra_content_items = items,
                                        recursive = True)
    self.assert_filename_list_equal( [
      f'{t.src_dir}/a/kiwi.jpg',
      f'{t.src_dir}/b/kiwi_dup1.jpg',
      f'{t.src_dir}/c/kiwi_dup2.jpg',
    ], t.result )

  def xtest_find_file_duplicates_no_dups(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'foo/cheese/brie.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'foo/cheese/cheddar.jpg', 'this is cheddar', 0o0644),
    ]
    t = self._call_find_file_duplicates('foo/cheese/cheddar.jpg',
                                        extra_content_items = items,
                                        recursive = True)
    self.assertEqual( [], t.result )

  def xtest_find_file_duplicates_with_setup(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'foo/cheese/brie.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'foo/cheese/cheddar.jpg', 'this is cheddar', 0o0644),
      temp_content('file', 'foo/cheese/gouda.jpg', 'this is lemon', 0o0644),
    ]
    options = bf_file_dups_finder_options(recursive = True)
    with dir_operation_tester(extra_content_items = items) as t:
      setup = file_duplicates.setup([ t.src_dir ], options = options)

      dups = file_duplicates.find_file_duplicates_with_setup(f'{t.tmp_dir}/foo/cheese/brie.jpg', setup)
      self.assert_filename_list_equal( [
        f'{t.src_dir}/a/kiwi.jpg',
        f'{t.src_dir}/b/kiwi_dup1.jpg',
        f'{t.src_dir}/c/kiwi_dup2.jpg',
      ], dups )

      dups = file_duplicates.find_file_duplicates_with_setup(f'{t.tmp_dir}/foo/cheese/gouda.jpg', setup)
      self.assert_filename_list_equal( [
        f'{t.src_dir}/a/lemon.jpg',
      ], dups )
      
  def xtest_find_file_duplicates_with_setup_and_removed_resolved_file(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'foo/cheese/brie.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'foo/cheese/cheddar.jpg', 'this is cheddar', 0o0644),
      temp_content('file', 'foo/cheese/gouda.jpg', 'this is lemon', 0o0644),
    ]
    options = bf_file_dups_finder_options(recursive = True)
    with dir_operation_tester(extra_content_items = items) as t:
      setup = file_duplicates.setup([ t.src_dir ], options = options)

      file_util.remove(f'{t.src_dir}/a/kiwi.jpg')
      
      dups = file_duplicates.find_file_duplicates_with_setup(f'{t.tmp_dir}/foo/cheese/brie.jpg', setup)
      self.assert_filename_list_equal( [
        f'{t.src_dir}/b/kiwi_dup1.jpg',
        f'{t.src_dir}/c/kiwi_dup2.jpg',
      ], dups )

      dups = file_duplicates.find_file_duplicates_with_setup(f'{t.tmp_dir}/foo/cheese/gouda.jpg', setup)
      self.assert_filename_list_equal( [
        f'{t.src_dir}/a/lemon.jpg',
      ], dups )
      
  def _call_find_duplicates(self): #,
                            #extra_content_items = None,
                            #recursive = False,
                            #small_checksum_size = 1024 * 1024,
                            #prefer_prefixes = None,
                            #sort_key = None,
                            #pre_test_function = None,
                            #include_empty_files = False,
                            #ignore_files = []):
    options = bf_file_dups_finder_options(recursive = recursive,
                                      small_checksum_size = small_checksum_size,
                                      sort_key = sort_key,
                                      include_empty_files = include_empty_files,
                                      ignore_files = ignore_files)
    with dir_operation_tester(extra_content_items = extra_content_items) as test:
      if pre_test_function:
        pre_test_function(test)
      if prefer_prefixes:
        xglobals = { 'test': test }
        prefer_prefixes = [ eval(x, xglobals) for x in prefer_prefixes ]
        options.prefer_prefixes = prefer_prefixes
      if True: #False:
        print(f'sort_key={sort_key}', flush = True)
        print('-----', flush = True)
        print(pprint.pformat(options.to_dict()), flush = True)
      test.result = file_duplicates.find_duplicates([ test.src_dir ],
                                                    options = options)
    return test

  def _call_setup(self,
                  extra_content_items = None,
                  recursive = False,
                  small_checksum_size = 1024 * 1024,
                  prefer_prefixes = None,
                  sort_key = None,
                  include_empty_files = False,
                  ignore_files = []):
    options = bf_file_dups_finder_options(recursive = recursive,
                                      small_checksum_size = small_checksum_size,
                                      sort_key = sort_key,
                                      include_empty_files = include_empty_files,
                                      ignore_files = ignore_files)
    if prefer_prefixes:
      xglobals = { 'test': test }
      prefer_prefixes = [ eval(x, xglobals) for x in prefer_prefixes ]
      options.prefer_prefixes = prefer_prefixes
    return file_duplicates.setup([ test.src_dir ], options = options)

  def _call_find_file_duplicates(self,
                                 filename,
                                 extra_content_items = None,
                                 recursive = False,
                                 small_checksum_size = 1024 * 1024,
                                 prefer_prefixes = None,
                                 sort_key = None,
                                 pre_test_function = None,
                                 include_empty_files = False,
                                 ignore_files = []):
    options = bf_file_dups_finder_options(recursive = recursive,
                                      small_checksum_size = small_checksum_size,
                                      sort_key = sort_key,
                                      include_empty_files = include_empty_files,
                                      ignore_files = ignore_files)
    with dir_operation_tester(extra_content_items = extra_content_items) as test:
      if pre_test_function:
        pre_test_function(test)
      if prefer_prefixes:
        xglobals = { 'test': test }
        prefer_prefixes = [ eval(x, xglobals) for x in prefer_prefixes ]
        options.prefer_prefixes = prefer_prefixes
      test.result = file_duplicates.find_file_duplicates(path.join(test.tmp_dir, filename),
                                                         [ test.src_dir ],
                                                         options = options)
    return test

  def _xp_result_item(self, item):
    return file_duplicates._dup_item(self.xp_filename(item[0], sep = path.sep),
                                     self.xp_filename_list(item[1], sep = path.sep))

  def _xp_result_item_list(self, items):
    return [ self._xp_result_item(item) for item in items ]
  
  def _xp_result(self, result):
    return file_duplicates._find_duplicates_result(self._xp_result_item_list(result.items),
                                                   result.resolved_files)
  
if __name__ == '__main__':
  unit_test.main()

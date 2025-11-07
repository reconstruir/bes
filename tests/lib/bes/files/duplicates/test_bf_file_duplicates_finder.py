#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from os import path
from datetime import datetime
from datetime import timedelta
from bes.files.bf_path import bf_path
from bes.files.bf_entry import bf_entry
from bes.files.duplicates.bf_file_duplicates_finder import bf_file_duplicates_finder
from bes.files.duplicates.bf_file_duplicates_finder_options import bf_file_duplicates_finder_options
from bes.files.duplicates.bf_file_duplicates_entry_list import bf_file_duplicates_entry_list
from bes.files.hashing.bf_hasher_hashlib import bf_hasher_hashlib
from bes.fs.testing.temp_content import temp_content
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class test_file_duplicates(unit_test):

  def test_resolve_files(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
    ]
    with dir_operation_tester(extra_content_items = items) as tester:
      hasher = bf_hasher_hashlib()
      finder = bf_file_duplicates_finder(hasher = hasher)
      resolved_files = finder.resolve_files(tester.src_dir)
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
      finder = bf_file_duplicates_finder(hasher = hasher)
      result = finder.find_duplicates([ tester.src_dir ])
      self.assert_json_equal( '''
{
  "resolved_entries": [
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
    },
    {
      "filename": "d/empty1.txt",
      "root_dir": "${root_dir}",
      "index": 5,
      "found_index": 5
    },
    {
      "filename": "e/empty2.txt",
      "root_dir": "${root_dir}",
      "index": 6,
      "found_index": 6
    }
  ],
  "duplicate_items": [
    {
      "entry": {
        "filename": "a/kiwi.jpg",
        "root_dir": "${root_dir}",
        "index": 1,
        "found_index": 1
      },
      "duplicates": [
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
    }
  ]
}
''', result.to_json(replacements = { tester.src_dir: '${root_dir}' }) )

  def test_find_duplicates_no_duplicates(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi 2', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi 3', 0o0644),
    ]
    with dir_operation_tester(extra_content_items = items) as tester:
      hasher = bf_hasher_hashlib()
      finder = bf_file_duplicates_finder(hasher = hasher)
      result = finder.find_duplicates([ tester.src_dir ])
      self.assert_json_equal( '''
{
  "resolved_entries": [
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
  ],
  "duplicate_items": []
}
''', result.to_json(replacements = { tester.src_dir: '${root_dir}' }) )

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
      options = bf_file_duplicates_finder_options(include_empty_files = True)
      finder = bf_file_duplicates_finder(hasher = hasher, options = options)
      result = finder.find_duplicates([ tester.src_dir ])
      self.assert_json_equal( '''
{
  "resolved_entries": [
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
    },
    {
      "filename": "d/empty1.txt",
      "root_dir": "${root_dir}",
      "index": 5,
      "found_index": 5
    },
    {
      "filename": "e/empty2.txt",
      "root_dir": "${root_dir}",
      "index": 6,
      "found_index": 6
    }
  ],
  "duplicate_items": [
    {
      "entry": {
        "filename": "a/kiwi.jpg",
        "root_dir": "${root_dir}",
        "index": 1,
        "found_index": 1
      },
      "duplicates": [
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
    },
    {
      "entry": {
        "filename": "d/empty1.txt",
        "root_dir": "${root_dir}",
        "index": 5,
        "found_index": 5
      },
      "duplicates": [
        {
          "filename": "e/empty2.txt",
          "root_dir": "${root_dir}",
          "index": 6,
          "found_index": 6
        }
      ]
    }
  ]
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
      options = bf_file_duplicates_finder_options(include_resource_forks = True)
      finder = bf_file_duplicates_finder(hasher = hasher, options = options)
      result = finder.find_duplicates([ tester.src_dir ])
      self.assert_json_equal( '''
{
  "resolved_entries": [
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
    },
    {
      "filename": "d/._empty1.txt",
      "root_dir": "${root_dir}",
      "index": 5,
      "found_index": 5
    },
    {
      "filename": "d/empty1.txt",
      "root_dir": "${root_dir}",
      "index": 6,
      "found_index": 6
    },
    {
      "filename": "e/._empty2.txt",
      "root_dir": "${root_dir}",
      "index": 7,
      "found_index": 7
    },
    {
      "filename": "e/empty2.txt",
      "root_dir": "${root_dir}",
      "index": 8,
      "found_index": 8
    }
  ],
  "duplicate_items": [
    {
      "entry": {
        "filename": "a/kiwi.jpg",
        "root_dir": "${root_dir}",
        "index": 1,
        "found_index": 1
      },
      "duplicates": [
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
    },
    {
      "entry": {
        "filename": "d/._empty1.txt",
        "root_dir": "${root_dir}",
        "index": 5,
        "found_index": 5
      },
      "duplicates": [
        {
          "filename": "e/._empty2.txt",
          "root_dir": "${root_dir}",
          "index": 7,
          "found_index": 7
        }
      ]
    }
  ]
}
''', result.to_json().replace(tester.src_dir, '${root_dir}') )

  def test_find_duplicates_with_prefer_prefixes(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/z/kiwi_dup3.jpg', 'this is kiwi', 0o0644),
    ]
    with dir_operation_tester(extra_content_items = items) as tester:
      hasher = bf_hasher_hashlib()
      prefer_prefixes = [ path.join(tester.src_dir, 'z') ]
      options = bf_file_duplicates_finder_options(prefer_prefixes = prefer_prefixes)
      finder = bf_file_duplicates_finder(hasher = hasher, options = options)
      result = finder.find_duplicates([ tester.src_dir ])
      self.assert_json_equal( '''
{
  "resolved_entries": [
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
    },
    {
      "filename": "z/kiwi_dup3.jpg",
      "root_dir": "${root_dir}",
      "index": 5,
      "found_index": 5
    }
  ],
  "duplicate_items": [
    {
      "entry": {
        "filename": "z/kiwi_dup3.jpg",
        "root_dir": "${root_dir}",
        "index": 5,
        "found_index": 5
      },
      "duplicates": [
        {
          "filename": "a/kiwi.jpg",
          "root_dir": "${root_dir}",
          "index": 1,
          "found_index": 1
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
    }
  ]
}
''', result.to_json().replace(tester.src_dir, '${root_dir}') )

  def test_find_duplicates_with_sort_key(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/z/kiwi_dup3.jpg', 'this is kiwi', 0o0644),
    ]
    with dir_operation_tester(extra_content_items = items) as tester:
      hasher = bf_hasher_hashlib()
      sort_key = lambda entry: [ 0 if 'z' in entry.filename_split else 1 ]
      options = bf_file_duplicates_finder_options(sort_key = sort_key)
      finder = bf_file_duplicates_finder(hasher = hasher, options = options)
      result = finder.find_duplicates([ tester.src_dir ])
      self.assert_json_equal( '''
{
  "resolved_entries": [
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
    },
    {
      "filename": "z/kiwi_dup3.jpg",
      "root_dir": "${root_dir}",
      "index": 5,
      "found_index": 5
    }
  ],
  "duplicate_items": [
    {
      "entry": {
        "filename": "z/kiwi_dup3.jpg",
        "root_dir": "${root_dir}",
        "index": 5,
        "found_index": 5
      },
      "duplicates": [
        {
          "filename": "a/kiwi.jpg",
          "root_dir": "${root_dir}",
          "index": 1,
          "found_index": 1
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
    }
  ]
}
''', result.to_json().replace(tester.src_dir, '${root_dir}') )
      
  def test_find_duplicates_with_ignore_filename(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/d/kiwi_dup3.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/d/.testing_test_ignore', 'kiwi_dup3.jpg\n', 0o0644),
      temp_content('file', 'src/d/empty1.txt', '', 0o0644),
      temp_content('resource_fork', 'src/d/._empty1.txt', '', 0o0644),
      temp_content('file', 'src/e/empty2.txt', '', 0o0644),
      temp_content('resource_fork', 'src/e/._empty2.txt', '', 0o0644),
    ]
    with dir_operation_tester(extra_content_items = items) as tester:
      hasher = bf_hasher_hashlib()
      options = bf_file_duplicates_finder_options(ignore_filename = '.testing_test_ignore')
      finder = bf_file_duplicates_finder(hasher = hasher, options = options)
      result = finder.find_duplicates([ tester.src_dir ])
      self.assert_json_equal( '''
{
  "resolved_entries": [
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
    },
    {
      "filename": "d/empty1.txt",
      "root_dir": "${root_dir}",
      "index": 5,
      "found_index": 5
    },
    {
      "filename": "e/empty2.txt",
      "root_dir": "${root_dir}",
      "index": 6,
      "found_index": 6
    }
  ],
  "duplicate_items": [
    {
      "entry": {
        "filename": "a/kiwi.jpg",
        "root_dir": "${root_dir}",
        "index": 1,
        "found_index": 1
      },
      "duplicates": [
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
    }
  ]
}
''', result.to_json().replace(tester.src_dir, '${root_dir}') )
      
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
                                   sort_key = bf_file_duplicates_finder_options.sort_key_basename_length)
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
                                   sort_key = bf_file_duplicates_finder_options.sort_key_modification_date,
                                   pre_test_function = _ptf)
    self.assertEqual( self._xp_result_item_list([
      ( f'{t.src_dir}/a/kiwi_03.jpg', [
        f'{t.src_dir}/b/kiwi_02.jpg',
        f'{t.src_dir}/c/kiwi_01.jpg',
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

  def test_find_duplicates_for_entry_basic(self):
    items = [
      temp_content('file', 'src/a/kiwi.txt', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.txt', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.txt', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.txt', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.txt', 'this is kiwi', 0o0644),
      temp_content('file', 'src/d/kiwi_dup3.txt', 'this is kiwi', 0o0644),
    ]
    with dir_operation_tester(extra_content_items = items) as tester:
      hasher = bf_hasher_hashlib()
      finder = bf_file_duplicates_finder(hasher = hasher)
      tmp_file = self.make_temp_file(content = 'this is kiwi', suffix = '.txt')
      entry = bf_entry(tmp_file)
      result = finder.find_duplicates_for_entry(entry, [ tester.src_dir ])
      self.assert_json_equal( '''
{
  "resolved_entries": [
    {
      "filename": "a/apple.txt",
      "root_dir": "${root_dir}",
      "index": 0,
      "found_index": 0
    },
    {
      "filename": "a/kiwi.txt",
      "root_dir": "${root_dir}",
      "index": 1,
      "found_index": 1
    },
    {
      "filename": "a/lemon.txt",
      "root_dir": "${root_dir}",
      "index": 2,
      "found_index": 2
    },
    {
      "filename": "b/kiwi_dup1.txt",
      "root_dir": "${root_dir}",
      "index": 3,
      "found_index": 3
    },
    {
      "filename": "c/kiwi_dup2.txt",
      "root_dir": "${root_dir}",
      "index": 4,
      "found_index": 4
    },
    {
      "filename": "d/kiwi_dup3.txt",
      "root_dir": "${root_dir}",
      "index": 5,
      "found_index": 5
    }
  ],
  "duplicate_items": [
    {
      "entry": {
        "filename": "${tmp_file}",
        "root_dir": null
      },
      "duplicates": [
        {
          "filename": "a/kiwi.txt",
          "root_dir": "${root_dir}",
          "index": 1,
          "found_index": 1
        },
        {
          "filename": "b/kiwi_dup1.txt",
          "root_dir": "${root_dir}",
          "index": 3,
          "found_index": 3
        },
        {
          "filename": "c/kiwi_dup2.txt",
          "root_dir": "${root_dir}",
          "index": 4,
          "found_index": 4
        },
        {
          "filename": "d/kiwi_dup3.txt",
          "root_dir": "${root_dir}",
          "index": 5,
          "found_index": 5
        }
      ]
    }
  ]
}
''', result.to_json(replacements = { tester.src_dir: '${root_dir}', tmp_file: '${tmp_file}' }) )
    
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
    options = bf_file_duplicates_finder_options(recursive = True)
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

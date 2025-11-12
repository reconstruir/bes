#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from os import path
from datetime import datetime
from datetime import timedelta
from bes.property.cached_property import cached_property
from bes.files.bf_path import bf_path
from bes.files.bf_entry import bf_entry
from bes.files.bf_file_ops import bf_file_ops
from bes.files.duplicates.bf_file_duplicates_finder import bf_file_duplicates_finder
from bes.files.duplicates.bf_file_duplicates_finder_options import bf_file_duplicates_finder_options
from bes.files.duplicates.bf_file_duplicates_entry_list import bf_file_duplicates_entry_list
from bes.files.hashing.bf_hasher_hashlib import bf_hasher_hashlib
from bes.fs.testing.temp_content import temp_content
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class _file_duplicates_finder_tester(dir_operation_tester):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.options = None

  @cached_property
  def finder(self):
    hasher = hasher = bf_hasher_hashlib()
    return bf_file_duplicates_finder(hasher = hasher, options = self.options)

  def resolve_files_as_json(self):
    resolved_files = self.finder.resolve_files(self.src_dir)
    replacements = {
      self.src_dir: '${root_dir}',
    }
    return resolved_files.to_json(replacements = replacements,
                                  xp_filenames = True)

  def find_duplicates_as_json(self, **kwargs):
    result = self.finder.find_duplicates(**kwargs)
    replacements = {
      self.src_dir: '${root_dir}',
    }
    return result.to_json(replacements = replacements,
                          xp_filenames = True)

class test_bf_file_duplicates_finder(unit_test):

  def test_resolve_files(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
    ]
    with _file_duplicates_finder_tester(extra_content_items = items) as tester:
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
''', tester.resolve_files_as_json() )

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
    with _file_duplicates_finder_tester(extra_content_items = items) as tester:
      self.assert_json_equal( '''
{
  "duplicate_items": [
    {
      "duplicates": [
        {
          "filename": "b/kiwi_dup1.jpg",
          "found_index": 3,
          "index": 3,
          "root_dir": "${root_dir}"
        },
        {
          "filename": "c/kiwi_dup2.jpg",
          "found_index": 4,
          "index": 4,
          "root_dir": "${root_dir}"
        }
      ],
      "entry": {
        "filename": "a/kiwi.jpg",
        "found_index": 1,
        "index": 1,
        "root_dir": "${root_dir}"
      }
    }
  ],
  "resolved_entries": [
    {
      "filename": "a/apple.jpg",
      "found_index": 0,
      "index": 0,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "a/kiwi.jpg",
      "found_index": 1,
      "index": 1,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "a/lemon.jpg",
      "found_index": 2,
      "index": 2,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "b/kiwi_dup1.jpg",
      "found_index": 3,
      "index": 3,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "c/kiwi_dup2.jpg",
      "found_index": 4,
      "index": 4,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "d/empty1.txt",
      "found_index": 5,
      "index": 5,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "e/empty2.txt",
      "found_index": 6,
      "index": 6,
      "root_dir": "${root_dir}"
    }
  ]
}
''', tester.find_duplicates_as_json(where = [ tester.src_dir ]) )

  def test_find_duplicates_with_resolved_entries(self):
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
    with _file_duplicates_finder_tester(extra_content_items = items) as tester:
      resolved_entries = tester.finder.resolve_files(tester.src_dir)
      self.assert_json_equal( '''
{
  "duplicate_items": [
    {
      "duplicates": [
        {
          "filename": "b/kiwi_dup1.jpg",
          "found_index": 3,
          "index": 3,
          "root_dir": "${root_dir}"
        },
        {
          "filename": "c/kiwi_dup2.jpg",
          "found_index": 4,
          "index": 4,
          "root_dir": "${root_dir}"
        }
      ],
      "entry": {
        "filename": "a/kiwi.jpg",
        "found_index": 1,
        "index": 1,
        "root_dir": "${root_dir}"
      }
    }
  ],
  "resolved_entries": [
    {
      "filename": "a/apple.jpg",
      "found_index": 0,
      "index": 0,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "a/kiwi.jpg",
      "found_index": 1,
      "index": 1,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "a/lemon.jpg",
      "found_index": 2,
      "index": 2,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "b/kiwi_dup1.jpg",
      "found_index": 3,
      "index": 3,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "c/kiwi_dup2.jpg",
      "found_index": 4,
      "index": 4,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "d/empty1.txt",
      "found_index": 5,
      "index": 5,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "e/empty2.txt",
      "found_index": 6,
      "index": 6,
      "root_dir": "${root_dir}"
    }
  ]
}
''', tester.find_duplicates_as_json(resolved_entries = resolved_entries) )
      
  def test_find_duplicates_no_duplicates(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi 2', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi 3', 0o0644),
    ]
    with _file_duplicates_finder_tester(extra_content_items = items) as tester:
      self.assert_json_equal( '''
{
  "duplicate_items": [],
  "resolved_entries": [
    {
      "filename": "a/apple.jpg",
      "found_index": 0,
      "index": 0,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "a/kiwi.jpg",
      "found_index": 1,
      "index": 1,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "a/lemon.jpg",
      "found_index": 2,
      "index": 2,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "b/kiwi_dup1.jpg",
      "found_index": 3,
      "index": 3,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "c/kiwi_dup2.jpg",
      "found_index": 4,
      "index": 4,
      "root_dir": "${root_dir}"
    }
  ]
}
''', tester.find_duplicates_as_json(where = [ tester.src_dir ]) )
      
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
    with _file_duplicates_finder_tester(extra_content_items = items) as tester:
      tester.options = bf_file_duplicates_finder_options(include_empty_files = True)
      self.assert_json_equal( '''
{
  "duplicate_items": [
    {
      "duplicates": [
        {
          "filename": "b/kiwi_dup1.jpg",
          "found_index": 3,
          "index": 3,
          "root_dir": "${root_dir}"
        },
        {
          "filename": "c/kiwi_dup2.jpg",
          "found_index": 4,
          "index": 4,
          "root_dir": "${root_dir}"
        }
      ],
      "entry": {
        "filename": "a/kiwi.jpg",
        "found_index": 1,
        "index": 1,
        "root_dir": "${root_dir}"
      }
    },
    {
      "duplicates": [
        {
          "filename": "e/empty2.txt",
          "found_index": 6,
          "index": 6,
          "root_dir": "${root_dir}"
        }
      ],
      "entry": {
        "filename": "d/empty1.txt",
        "found_index": 5,
        "index": 5,
        "root_dir": "${root_dir}"
      }
    }
  ],
  "resolved_entries": [
    {
      "filename": "a/apple.jpg",
      "found_index": 0,
      "index": 0,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "a/kiwi.jpg",
      "found_index": 1,
      "index": 1,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "a/lemon.jpg",
      "found_index": 2,
      "index": 2,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "b/kiwi_dup1.jpg",
      "found_index": 3,
      "index": 3,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "c/kiwi_dup2.jpg",
      "found_index": 4,
      "index": 4,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "d/empty1.txt",
      "found_index": 5,
      "index": 5,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "e/empty2.txt",
      "found_index": 6,
      "index": 6,
      "root_dir": "${root_dir}"
    }
  ]
}
''', tester.find_duplicates_as_json(where = [ tester.src_dir ]) )

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
    with _file_duplicates_finder_tester(extra_content_items = items) as tester:
      tester.options = bf_file_duplicates_finder_options(include_resource_forks = True)
      self.assert_json_equal( '''
{
  "duplicate_items": [
    {
      "duplicates": [
        {
          "filename": "b/kiwi_dup1.jpg",
          "found_index": 3,
          "index": 3,
          "root_dir": "${root_dir}"
        },
        {
          "filename": "c/kiwi_dup2.jpg",
          "found_index": 4,
          "index": 4,
          "root_dir": "${root_dir}"
        }
      ],
      "entry": {
        "filename": "a/kiwi.jpg",
        "found_index": 1,
        "index": 1,
        "root_dir": "${root_dir}"
      }
    },
    {
      "duplicates": [
        {
          "filename": "e/._empty2.txt",
          "found_index": 7,
          "index": 7,
          "root_dir": "${root_dir}"
        }
      ],
      "entry": {
        "filename": "d/._empty1.txt",
        "found_index": 5,
        "index": 5,
        "root_dir": "${root_dir}"
      }
    }
  ],
  "resolved_entries": [
    {
      "filename": "a/apple.jpg",
      "found_index": 0,
      "index": 0,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "a/kiwi.jpg",
      "found_index": 1,
      "index": 1,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "a/lemon.jpg",
      "found_index": 2,
      "index": 2,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "b/kiwi_dup1.jpg",
      "found_index": 3,
      "index": 3,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "c/kiwi_dup2.jpg",
      "found_index": 4,
      "index": 4,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "d/._empty1.txt",
      "found_index": 5,
      "index": 5,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "d/empty1.txt",
      "found_index": 6,
      "index": 6,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "e/._empty2.txt",
      "found_index": 7,
      "index": 7,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "e/empty2.txt",
      "found_index": 8,
      "index": 8,
      "root_dir": "${root_dir}"
    }
  ]
}
''', tester.find_duplicates_as_json(where = [ tester.src_dir ]) )

  def test_find_duplicates_with_prefer_prefixes(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/z/kiwi_dup3.jpg', 'this is kiwi', 0o0644),
    ]
    with _file_duplicates_finder_tester(extra_content_items = items) as tester:
      prefer_prefixes = [ path.join(tester.src_dir, 'z') ]
      tester.options = bf_file_duplicates_finder_options(prefer_prefixes = prefer_prefixes)
      result = tester.finder.find_duplicates(where = [ tester.src_dir ])
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
    with _file_duplicates_finder_tester(extra_content_items = items) as tester:
      sort_key = lambda entry: [ 0 if 'z' in entry.filename_split else 1 ]
      tester.options = bf_file_duplicates_finder_options(sort_key = sort_key)
      result = tester.finder.find_duplicates(where = [ tester.src_dir ])
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
    with _file_duplicates_finder_tester(extra_content_items = items) as tester:
      tester.options = bf_file_duplicates_finder_options(ignore_filename = '.testing_test_ignore')
      result = tester.finder.find_duplicates(where = [ tester.src_dir ])
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
    with _file_duplicates_finder_tester(extra_content_items = items) as tester:
      tmp_file = self.make_temp_file(content = 'this is kiwi', suffix = '.txt')
      entry = bf_entry(tmp_file)
      result = tester.finder.find_duplicates_for_entry(entry, where = [ tester.src_dir ])
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

  def test_find_duplicates_for_entry_no_match(self):
    items = [
      temp_content('file', 'src/a/kiwi.txt', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.txt', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.txt', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.txt', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.txt', 'this is kiwi', 0o0644),
      temp_content('file', 'src/d/kiwi_dup3.txt', 'this is kiwi', 0o0644),
    ]
    with _file_duplicates_finder_tester(extra_content_items = items) as tester:
      tmp_file = self.make_temp_file(content = 'this is not kiwi', suffix = '.txt')
      entry = bf_entry(tmp_file)
      result = tester.finder.find_duplicates_for_entry(entry, where = [ tester.src_dir ])
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
      "duplicates": []
    }
  ]
}
''', result.to_json(replacements = { tester.src_dir: '${root_dir}', tmp_file: '${tmp_file}' }) )
      
  def test_find_duplicates_with_resolve_files_removed_file(self):
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
    with _file_duplicates_finder_tester(extra_content_items = items) as tester:
      resolved_entries = tester.finder.resolve_files(tester.src_dir)
      bf_file_ops.remove(f'{tester.src_dir}/a/kiwi.jpg')
      result = tester.finder.find_duplicates(resolved_entries = resolved_entries)
      self.assert_json_equal( '''
{
  "duplicate_items": [
    {
      "duplicates": [
        {
          "filename": "c/kiwi_dup2.jpg",
          "found_index": 3,
          "index": 3,
          "root_dir": "${root_dir}"
        }
      ],
      "entry": {
        "filename": "b/kiwi_dup1.jpg",
        "found_index": 2,
        "index": 2,
        "root_dir": "${root_dir}"
      }
    }
  ],
  "resolved_entries": [
    {
      "filename": "a/apple.jpg",
      "found_index": 0,
      "index": 0,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "a/lemon.jpg",
      "found_index": 1,
      "index": 1,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "b/kiwi_dup1.jpg",
      "found_index": 2,
      "index": 2,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "c/kiwi_dup2.jpg",
      "found_index": 3,
      "index": 3,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "d/empty1.txt",
      "found_index": 4,
      "index": 4,
      "root_dir": "${root_dir}"
    },
    {
      "filename": "e/empty2.txt",
      "found_index": 5,
      "index": 5,
      "root_dir": "${root_dir}"
    }
  ]
}
''', tester.find_duplicates_as_json(where = [ tester.src_dir ]) )
  
if __name__ == '__main__':
  unit_test.main()

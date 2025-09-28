#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.json_util import json_util
from bes.files.bf_entry import bf_entry
from bes.files.find.bf_file_finder import bf_file_finder
from bes.files.duplicates.bf_file_dups_entry_list import bf_file_dups_entry_list
from bes.files.hashing.bf_hasher_hashlib import bf_hasher_hashlib
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from bes.fs.testing.temp_content import temp_content

class _bf_entry_list_tester(object):

  def __init__(self, content, where = None):
    self._tmp_dir = self._make_temp_content(content)
    if where:
      find_where = [ path.join(self._tmp_dir, nw) for nw in where ]
    else:
      find_where = self._tmp_dir
    self._find_result = bf_file_finder.find_with_options(find_where,
                                                         entry_list_class = bf_file_dups_entry_list)

  @property
  def tmp_dir(self):
    return self._tmp_dir

  @property
  def entries(self):
    return self._find_result.entries

  def make_entry(self, fragment):
    return bf_entry(path.join(self.tmp_dir, fragment))
  
  @classmethod
  def _make_temp_content(clazz, content):
    return temp_content.write_items_to_temp_dir(content, delete = not test_bf_file_dups_entry_list.DEBUG)

  def checksum_map_as_json(self):
    cm = self.entries.checksum_map(bf_hasher_hashlib(), 'sha256')
    json_text = json_util.to_json(cm, indent = 2, sort_keys = True)
    return json_text.replace(self._tmp_dir, '${tmp_dir}')

  def short_checksum_map_as_json(self):
    cm = self.entries.short_checksum_map(bf_hasher_hashlib(), 'sha256')
    json_text = json_util.to_json(cm, indent = 2, sort_keys = True)
    return json_text.replace(self._tmp_dir, '${tmp_dir}')
  
class test_bf_file_dups_entry_list(unit_test):
  
  def _make_test_entry(self, *args, **kargs):
    tmp = self.make_temp_file(*args, **kargs)
    return bf_entry(tmp)

  def _make_test_entry_dir(self, *args, **kargs):
    tmp = self.make_temp_dir(*args, **kargs)
    return bf_entry(tmp)

  def _make_test_entry_link(self, *args, **kargs):
    tmp1 = self.make_temp_file(*args, **kargs)
    tmp2 = self.make_temp_file(suffix = '-two')
    filesystem.remove(tmp2)
    os.symlink(tmp1, tmp2)
    return bf_entry(tmp2)

  def _make_tmp_dir(self):
    return self.make_temp_dir(prefix = 'test_bf_file_dups_entry_list_', suffix = '.dir')

  def _make_test_entry_root_dir(self, root_dir, fragment, basename):
    filename = path.join(fragment, basename)
    return bf_entry(filename, root_dir = root_dir)
    
  def test_checksum_map(self):
    brie_tmp = self.make_temp_file(content = 'brie.cheese' * 200000)
    cheddar_tmp = self.make_temp_file(content = 'cheddar.cheese' * 200000)
    kiwi_tmp = self.make_temp_file(content = 'kiwi.fruit' * 200000)
    lemon_tmp = self.make_temp_file(content = 'lemon.cheese' * 200000)
    t = _bf_entry_list_tester([
      f'file foo/fruit/lemon.fruit "file:{lemon_tmp}"',
      f'file foo/fruit/kiwi.fruit "file:{kiwi_tmp}"',
      f'file foo/cheese/brie.cheese "file:{brie_tmp}"',
      f'file bar/fruit/kiwi.fruit "file:{kiwi_tmp}"',
      f'file bar/cheese/brie.cheese "file:{brie_tmp}"',
      f'file bar/cheese/cheddar.cheese "file:{cheddar_tmp}"',
    ], where = [ 'foo', 'bar' ])
    self.assert_json_equal( '''
{
  "3d8c33d567ed80a3aec1f02c29d649d85839617ed2430efd374ae0f1ff231f91": {
    "_values": [
      {
        "_filename": "cheese/cheddar.cheese",
        "_root_dir": "${tmp_dir}/bar",
        "absolute_filename": "${tmp_dir}/bar/cheese/cheddar.cheese",
        "filename": "${tmp_dir}/bar/cheese/cheddar.cheese",
        "relative_filename": "cheese/cheddar.cheese"
      }
    ]
  },
  "5a7a0d61de3ad93b4d29664496781e792128a097c1f233234b43210254d7699e": {
    "_values": [
      {
        "_filename": "fruit/lemon.fruit",
        "_root_dir": "${tmp_dir}/foo",
        "absolute_filename": "${tmp_dir}/foo/fruit/lemon.fruit",
        "filename": "${tmp_dir}/foo/fruit/lemon.fruit",
        "relative_filename": "fruit/lemon.fruit"
      }
    ]
  },
  "98d4cb8bfd2a0adc645e1b56d9a1353afabee286b8dc55406fb31077d686d355": {
    "_values": [
      {
        "_filename": "cheese/brie.cheese",
        "_root_dir": "${tmp_dir}/bar",
        "absolute_filename": "${tmp_dir}/bar/cheese/brie.cheese",
        "filename": "${tmp_dir}/bar/cheese/brie.cheese",
        "relative_filename": "cheese/brie.cheese"
      },
      {
        "_filename": "cheese/brie.cheese",
        "_root_dir": "${tmp_dir}/foo",
        "absolute_filename": "${tmp_dir}/foo/cheese/brie.cheese",
        "filename": "${tmp_dir}/foo/cheese/brie.cheese",
        "relative_filename": "cheese/brie.cheese"
      }
    ]
  },
  "cedf6390305749237858b7f7061a131e5b2407c826f1f2a1afb4667c7e5fbc15": {
    "_values": [
      {
        "_filename": "fruit/kiwi.fruit",
        "_root_dir": "${tmp_dir}/bar",
        "absolute_filename": "${tmp_dir}/bar/fruit/kiwi.fruit",
        "filename": "${tmp_dir}/bar/fruit/kiwi.fruit",
        "relative_filename": "fruit/kiwi.fruit"
      },
      {
        "_filename": "fruit/kiwi.fruit",
        "_root_dir": "${tmp_dir}/foo",
        "absolute_filename": "${tmp_dir}/foo/fruit/kiwi.fruit",
        "filename": "${tmp_dir}/foo/fruit/kiwi.fruit",
        "relative_filename": "fruit/kiwi.fruit"
      }
    ]
  }
}
''', t.checksum_map_as_json() )

  def test_short_checksum_map(self):
    brie_tmp = self.make_temp_file(content = 'brie.cheese' * 200000)
    cheddar_tmp = self.make_temp_file(content = 'cheddar.cheese' * 200000)
    kiwi_tmp = self.make_temp_file(content = 'kiwi.fruit' * 200000)
    lemon_tmp = self.make_temp_file(content = 'lemon.cheese' * 200000)
    t = _bf_entry_list_tester([
      f'file foo/fruit/lemon.fruit "file:{lemon_tmp}"',
      f'file foo/fruit/kiwi.fruit "file:{kiwi_tmp}"',
      f'file foo/cheese/brie.cheese "file:{brie_tmp}"',
      f'file bar/fruit/kiwi.fruit "file:{kiwi_tmp}"',
      f'file bar/cheese/brie.cheese "file:{brie_tmp}"',
      f'file bar/cheese/cheddar.cheese "file:{cheddar_tmp}"',
    ], where = [ 'foo', 'bar' ])
    self.assert_json_equal( '''
{
  "b78b51fc10a1b3947d3de469f582c6dbb976642b2d0fd739665f2240df24cbbf": {
    "_values": [
      {
        "_filename": "fruit/kiwi.fruit",
        "_root_dir": "${tmp_dir}/bar",
        "absolute_filename": "${tmp_dir}/bar/fruit/kiwi.fruit",
        "filename": "${tmp_dir}/bar/fruit/kiwi.fruit",
        "relative_filename": "fruit/kiwi.fruit"
      },
      {
        "_filename": "fruit/kiwi.fruit",
        "_root_dir": "${tmp_dir}/foo",
        "absolute_filename": "${tmp_dir}/foo/fruit/kiwi.fruit",
        "filename": "${tmp_dir}/foo/fruit/kiwi.fruit",
        "relative_filename": "fruit/kiwi.fruit"
      }
    ]
  },
  "bef3fb54553181092d38d9520059740b9d516bbdb6869469b997d5547f552297": {
    "_values": [
      {
        "_filename": "fruit/lemon.fruit",
        "_root_dir": "${tmp_dir}/foo",
        "absolute_filename": "${tmp_dir}/foo/fruit/lemon.fruit",
        "filename": "${tmp_dir}/foo/fruit/lemon.fruit",
        "relative_filename": "fruit/lemon.fruit"
      }
    ]
  },
  "cad7aab0deebe28c02c0af3561db03a23fc7d7189e33add2b42f1604837260b0": {
    "_values": [
      {
        "_filename": "cheese/cheddar.cheese",
        "_root_dir": "${tmp_dir}/bar",
        "absolute_filename": "${tmp_dir}/bar/cheese/cheddar.cheese",
        "filename": "${tmp_dir}/bar/cheese/cheddar.cheese",
        "relative_filename": "cheese/cheddar.cheese"
      }
    ]
  },
  "d40fcfedf10603b4814ca7e13daf571c0b82b8240ac219df5fce0f97e5ee6287": {
    "_values": [
      {
        "_filename": "cheese/brie.cheese",
        "_root_dir": "${tmp_dir}/bar",
        "absolute_filename": "${tmp_dir}/bar/cheese/brie.cheese",
        "filename": "${tmp_dir}/bar/cheese/brie.cheese",
        "relative_filename": "cheese/brie.cheese"
      },
      {
        "_filename": "cheese/brie.cheese",
        "_root_dir": "${tmp_dir}/foo",
        "absolute_filename": "${tmp_dir}/foo/cheese/brie.cheese",
        "filename": "${tmp_dir}/foo/cheese/brie.cheese",
        "relative_filename": "cheese/brie.cheese"
      }
    ]
  }
}
''', t.short_checksum_map_as_json() )

  def test_basename_map(self):
    t = _bf_entry_list_tester([
      'file foo/fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file foo/cheese/brie.cheese "this is brie.cheese\n"',
      'file bar/fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file bar/cheese/brie.cheese "this is brie.cheese\n"',
    ], where = [ 'foo', 'bar' ])
    m = t.entries.basename_map()
    self.assertEqual( { 'brie.cheese', 'kiwi.fruit' }, m.keys() )
    self.assert_json_equal( '''
[
  {
    "filename": "cheese/brie.cheese",
    "root_dir": "${tmp_dir}/bar"
  },
  {
    "filename": "cheese/brie.cheese",
    "root_dir": "${tmp_dir}/foo"
  }
]
''', m['brie.cheese'].to_json(replacements = { t.tmp_dir: '${tmp_dir}' }) )
    
    self.assert_json_equal( '''
[
  {
    "filename": "fruit/kiwi.fruit",
    "root_dir": "${tmp_dir}/bar"
  },
  {
    "filename": "fruit/kiwi.fruit",
    "root_dir": "${tmp_dir}/foo"
  }
]
''', m['kiwi.fruit'].to_json(replacements = { t.tmp_dir: '${tmp_dir}' }) )

  def test_size_map(self):
    t = _bf_entry_list_tester([
      'file foo/fruit/lemon.fruit "this is lemon.fruit\n"',
      'file foo/fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file foo/cheese/brie.cheese "this is brie.cheese\n"',
      'file bar/fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file bar/cheese/brie.cheese "this is brie.cheese\n"',
      'file bar/cheese/cheddar.cheese "this is cheddar.cheese\n"',
    ], where = [ 'foo', 'bar' ])
    json_util.to_json(t.entries.size_map(), indent = 2, sort_keys = True)
    self.assert_json_equal( '''
{
  "19": {
    "_values": [
      {
        "_filename": "fruit/kiwi.fruit",
        "_root_dir": "${tmp_dir}/bar",
        "absolute_filename": "${tmp_dir}/bar/fruit/kiwi.fruit",
        "filename": "${tmp_dir}/bar/fruit/kiwi.fruit",
        "relative_filename": "fruit/kiwi.fruit"
      },
      {
        "_filename": "fruit/kiwi.fruit",
        "_root_dir": "${tmp_dir}/foo",
        "absolute_filename": "${tmp_dir}/foo/fruit/kiwi.fruit",
        "filename": "${tmp_dir}/foo/fruit/kiwi.fruit",
        "relative_filename": "fruit/kiwi.fruit"
      }
    ]
  },
  "20": {
    "_values": [
      {
        "_filename": "cheese/brie.cheese",
        "_root_dir": "${tmp_dir}/bar",
        "absolute_filename": "${tmp_dir}/bar/cheese/brie.cheese",
        "filename": "${tmp_dir}/bar/cheese/brie.cheese",
        "relative_filename": "cheese/brie.cheese"
      },
      {
        "_filename": "cheese/brie.cheese",
        "_root_dir": "${tmp_dir}/foo",
        "absolute_filename": "${tmp_dir}/foo/cheese/brie.cheese",
        "filename": "${tmp_dir}/foo/cheese/brie.cheese",
        "relative_filename": "cheese/brie.cheese"
      },
      {
        "_filename": "fruit/lemon.fruit",
        "_root_dir": "${tmp_dir}/foo",
        "absolute_filename": "${tmp_dir}/foo/fruit/lemon.fruit",
        "filename": "${tmp_dir}/foo/fruit/lemon.fruit",
        "relative_filename": "fruit/lemon.fruit"
      }
    ]
  },
  "23": {
    "_values": [
      {
        "_filename": "cheese/cheddar.cheese",
        "_root_dir": "${tmp_dir}/bar",
        "absolute_filename": "${tmp_dir}/bar/cheese/cheddar.cheese",
        "filename": "${tmp_dir}/bar/cheese/cheddar.cheese",
        "relative_filename": "cheese/cheddar.cheese"
      }
    ]
  }
}''', json_util.to_json(t.entries.size_map(), indent = 2, sort_keys = True).replace(t.tmp_dir, '${tmp_dir}') )

  def test_duplicate_size_map(self):
    t = _bf_entry_list_tester([
      'file foo/fruit/lemon.fruit "this is lemon.fruit\n"',
      'file foo/fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file foo/cheese/brie.cheese "this is brie.cheese\n"',
      'file bar/fruit/kiwi.fruit "this is kiwi.fruit\n"',
      'file bar/cheese/brie.cheese "this is brie.cheese\n"',
      'file bar/cheese/cheddar.cheese "this is cheddar.cheese\n"',
    ], where = [ 'foo', 'bar' ])
    json_util.to_json(t.entries.size_map(), indent = 2, sort_keys = True)
    self.assert_json_equal( '''
{
  "19": {
    "_values": [
      {
        "_filename": "fruit/kiwi.fruit",
        "_root_dir": "${tmp_dir}/bar",
        "absolute_filename": "${tmp_dir}/bar/fruit/kiwi.fruit",
        "filename": "${tmp_dir}/bar/fruit/kiwi.fruit",
        "relative_filename": "fruit/kiwi.fruit"
      },
      {
        "_filename": "fruit/kiwi.fruit",
        "_root_dir": "${tmp_dir}/foo",
        "absolute_filename": "${tmp_dir}/foo/fruit/kiwi.fruit",
        "filename": "${tmp_dir}/foo/fruit/kiwi.fruit",
        "relative_filename": "fruit/kiwi.fruit"
      }
    ]
  },
  "20": {
    "_values": [
      {
        "_filename": "cheese/brie.cheese",
        "_root_dir": "${tmp_dir}/bar",
        "absolute_filename": "${tmp_dir}/bar/cheese/brie.cheese",
        "filename": "${tmp_dir}/bar/cheese/brie.cheese",
        "relative_filename": "cheese/brie.cheese"
      },
      {
        "_filename": "cheese/brie.cheese",
        "_root_dir": "${tmp_dir}/foo",
        "absolute_filename": "${tmp_dir}/foo/cheese/brie.cheese",
        "filename": "${tmp_dir}/foo/cheese/brie.cheese",
        "relative_filename": "cheese/brie.cheese"
      },
      {
        "_filename": "fruit/lemon.fruit",
        "_root_dir": "${tmp_dir}/foo",
        "absolute_filename": "${tmp_dir}/foo/fruit/lemon.fruit",
        "filename": "${tmp_dir}/foo/fruit/lemon.fruit",
        "relative_filename": "fruit/lemon.fruit"
      }
    ]
  }
}''', json_util.to_json(t.entries.duplicate_size_map(), indent = 2, sort_keys = True).replace(t.tmp_dir, '${tmp_dir}') )
    
if __name__ == '__main__':
  unit_test.main()

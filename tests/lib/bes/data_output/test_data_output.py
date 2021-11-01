#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.compat.StringIO import StringIO
from bes.data_output.data_output import data_output
from bes.data_output.data_output_options import data_output_options
from bes.data_output.data_output_style import data_output_style
from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util

class test_data_output(unit_test):

  _fruit = namedtuple('fruit', 'name, color, flavor, size')

  _FRUITS = [
    _fruit('apple', 'red', 'sweet', 'medium'),
    _fruit('pear', 'green', 'sweet', 'medium'),
    _fruit('watermelon', 'red', 'sweet', 'large'),
    _fruit('lemon', 'yellow', 'tart', 'small'),
  ]
  
  def test_data_output_brief(self):
    self.assert_string_equal_fuzzy( '''\
apple
pear
watermelon
lemon
''', self._output(self._FRUITS, 'brief'),  )

  def test_data_output_table(self):
    self.assert_string_equal_fuzzy( '''\
+--------------------------------------+
| apple      | red    | sweet | medium |
| pear       | green  | sweet | medium |
| watermelon | red    | sweet | large  |
| lemon      | yellow | tart  | small  |
+--------------------------------------+
''', self._output(self._FRUITS, 'table'),  )

  def test_data_output_csv(self):
    self.assert_string_equal_fuzzy( '''\
apple,red,sweet,medium
pear,green,sweet,medium
watermelon,red,sweet,large
lemon,yellow,tart,small
''', self._output(self._FRUITS, 'csv'),  )

  def test_data_output_json(self):
    self.assert_string_equal_fuzzy( '''\
[
  {
    "color": "red",
    "flavor": "sweet",
    "name": "apple",
    "size": "medium"
  },
  {
    "color": "green",
    "flavor": "sweet",
    "name": "pear",
    "size": "medium"
  },
  {
    "color": "red",
    "flavor": "sweet",
    "name": "watermelon",
    "size": "large"
  },
  {
    "color": "yellow",
    "flavor": "tart",
    "name": "lemon",
    "size": "small"
  }
]
''', self._output(self._FRUITS, 'json'),  )
    
  def _output(self, data, style):
    tmp = self.make_temp_file()
    options = data_output_options(style = style,
                                  output_filename = tmp)
    data_output.output_table(data, options = options)
    return file_util.read(tmp, codec = 'utf-8')
    
if __name__ == '__main__':
  unit_test.main()

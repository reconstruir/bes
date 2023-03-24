#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.testing.unit_test import unit_test

from bes.files.bf_glob import bf_glob
from bes.fs.testing.temp_content import temp_content

class test_bf_glob(unit_test):

  def test_glob(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
      'file fruit/fruit.config         "fruits.config" 644',
      'file cheese/cheese.config       "cheese.config" 644',
      'file drinks/alcohol/wine.config "wine.config"   644',
      'file drinks/alcohol/beer.config "beer.config"   644',
      'file drinks/dairy/milk.config   "milk.config"   644',
      'file drinks/dairy/yogurt.config "yogurt.config" 644',
      'dir  nothing                 ""                 700',
    ])
    self.assert_filename_list_equal( [
      f'{tmp_dir}/drinks/alcohol/beer.config',
      f'{tmp_dir}/drinks/alcohol/wine.config',
    ], bf_glob.glob(path.join(tmp_dir, 'drinks/alcohol'), '*.config') )
    
  def test_glob_search_path(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
      'file fruit/fruit.config         "fruits.config" 644',
      'file cheese/cheese.config       "cheese.config" 644',
      'file drinks/alcohol/wine.config "wine.config"   644',
      'file drinks/alcohol/beer.config "beer.config"   644',
      'file drinks/dairy/milk.config   "milk.config"   644',
      'file drinks/dairy/yogurt.config "yogurt.config" 644',
      'dir  nothing                 ""                 700',
    ])
    search_path = [
      [ 'fruit' ],
      [ 'cheese' ],
      [ 'drinks', 'alcohol' ],
      [ 'drinks', 'dairy' ],
    ]
    search_path = [ path.join(tmp_dir, *x) for x in search_path ]
    self.assert_filename_list_equal( [
      f'{tmp_dir}/cheese/cheese.config',
      f'{tmp_dir}/drinks/alcohol/beer.config',
      f'{tmp_dir}/drinks/alcohol/wine.config',
      f'{tmp_dir}/drinks/dairy/milk.config',
      f'{tmp_dir}/drinks/dairy/yogurt.config',
      f'{tmp_dir}/fruit/fruit.config',
    ], bf_glob.glob(search_path, '*.config') )

  def xtest_glob_env_search_path(self):
    tmp_dir = temp_content.write_items_to_temp_dir([
      'file fruit/fruit.config         "fruits.config" 644',
      'file cheese/cheese.config       "cheese.config" 644',
      'file drinks/alcohol/wine.config "wine.config"   644',
      'file drinks/alcohol/beer.config "beer.config"   644',
      'file drinks/dairy/milk.config   "milk.config"   644',
      'file drinks/dairy/yogurt.config "yogurt.config" 644',
      'dir  nothing                 ""                 700',
    ])
    search_path = [
      [ 'fruit' ],
      [ 'cheese' ],
      [ 'drinks', 'alcohol' ],
      [ 'drinks', 'dairy' ],
    ]
    search_path = [ '{}/{}'.format(tmp_dir, path.join(x)) for x in search_path ]
    self.assert_filename_list_equal( [
      f'{tmp_dir}/cheese/cheese.config',
      f'{tmp_dir}/drinks/alcohol/beer.config',
      f'{tmp_dir}/drinks/alcohol/wine.config',
      f'{tmp_dir}/drinks/dairy/milk.config',
      f'{tmp_dir}/drinks/dairy/yogurt.config',
      f'{tmp_dir}/fruit/fruit.config',
    ], bf_glob.glob(search_path, '*.config') )

  def test_has_glob_pattern_true(self):
    self.assertTrue( bf_glob.has_glob_pattern('*.py') )
    self.assertTrue( bf_glob.has_glob_pattern('*.??') )

  def test_has_glob_pattern_false(self):
    self.assertFalse( bf_glob.has_glob_pattern('foo.py') )

if __name__ == '__main__':
  unit_test.main()

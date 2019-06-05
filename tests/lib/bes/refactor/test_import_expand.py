#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.refactor.import_expand import import_expand

class test_files(unit_test):

  _EXPAND_IMPORT_CONTENT = '''\
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, re

from collections import namedtuple

from bes.archive import archive, archiver
from bes.common import check, dict_util, json_util, string_util
from bes.property.cached_property import cached_property
from bes.fs import dir_util, file_check, file_find, file_search, file_replace, file_util, tar_util, temp_file
from bes.text import text_line_parser
from bes.match import matcher_filename, matcher_multiple_filename
from bes.python import setup_tools
from bes.system import execute, log
from rebuild.base import build_blurb, build_target, package_descriptor
from bes.debug import debug_timer

from rebuild.binary_format.binary_detector import binary_detector

from .package_metadata import package_metadata
from .package_manifest import package_manifest
from .package_file_list import package_file_list

class package(object):
  pass
'''
  
  def test_expand_text(self):
    text = '''\
from fruit.citrus import lemon, orange, lime
'''
    expected = '''\
from fruit.citrus import lemon
from fruit.citrus import orange
from fruit.citrus import lime
'''
    self.assertMultiLineEqual( expected, import_expand.expand_text('fruit', text, False) )
                      
  def test_expand_text_with_sort(self):
    text = '''\
from fruit.citrus import lemon, orange, lime
'''
    expected = '''\
from fruit.citrus import lemon
from fruit.citrus import lime
from fruit.citrus import orange
'''
    self.assertMultiLineEqual( expected, import_expand.expand_text('fruit', text, True) )
                      
if __name__ == "__main__":
  unit_test.main()

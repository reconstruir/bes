#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.refactor.import_expand import import_expand

class test_files(unit_test):

  _EXPAND_IMPORT_CONTENT = '''\
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, re

from collections import namedtuple

from bes.archive.archive import archive
from bes.archive.archiver import archiver
from bes.common.check import check
from bes.common.dict_util import dict_util
from bes.common.json_util import json_util
from bes.common.string_util import string_util
from bes.property.cached_property import cached_property
from bes.fs.dir_util import dir_util
from bes.fs.file_check import file_check
from bes.fs.file_find import file_find
from bes.fs.file_replace import file_replace
from bes.fs.file_search import file_search
from bes.fs.file_util import file_util
from bes.fs.tar_util import tar_util
from bes.fs.temp_file import temp_file
from bes.text import text_line_parser
from bes.match.matcher_filename import matcher_filename
from bes.match.matcher_multiple_filename import matcher_multiple_filename
from bes.python import setup_tools
from bes.system.execute import execute
from bes.system.log import log
from something.base import build_blurb, build_target, package_descriptor
from bes.debug import debug_timer

from something.binary_format.binary_detector import binary_detector

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
    self.assertMultiLineEqual( expected, import_expand.expand_text('fruit', text, False, False) )
                      
  def test_expand_text_with_sort(self):
    text = '''\
from fruit.citrus import lemon, orange, lime
'''
    expected = '''\
from fruit.citrus import lemon
from fruit.citrus import lime
from fruit.citrus import orange
'''
    self.assertMultiLineEqual( expected, import_expand.expand_text('fruit', text, True, False) )

  def test_expand_multiple(self):
    text = '''\
from fruit.citrus import lemon, orange, lime
from fruit.fiber import inulin
from fruit.cover import peel, skin
from fruit.sugar import fructose, xylitol
'''
    expected = '''\
from fruit.citrus import lemon
from fruit.citrus import orange
from fruit.citrus import lime
from fruit.fiber import inulin
from fruit.cover import peel
from fruit.cover import skin
from fruit.sugar import fructose
from fruit.sugar import xylitol
'''
    self.assertMultiLineEqual( expected, import_expand.expand_text('fruit', text, False, False) )
                      
  def test_expand_messier(self):
    text = '''\
import os.path as path, shutil
from fruit.system import exfoo, sbar
from collections import namedtuple
from baking.tools.frypan import cast_iron
from fruit.color import green, red, yellow
'''
    expected = '''\
import os.path as path, shutil
from fruit.system import exfoo
from fruit.system import sbar
from collections import namedtuple
from baking.tools.frypan import cast_iron
from fruit.color import green
from fruit.color import red
from fruit.color import yellow
'''
    self.assertMultiLineEqual( expected, import_expand.expand_text('fruit', text, False, False) )

  def test_expand_indentation(self):
    text = '''\
  class foo(object):
    def f(self):
      from fruit.color import green, red, yellow
'''
    expected = '''\
  class foo(object):
    def f(self):
      from fruit.color import green
      from fruit.color import red
      from fruit.color import yellow
'''
    self.assertMultiLineEqual( expected, import_expand.expand_text('fruit', text, False, False) )

  def test_expand_text_include_module(self):
    text = '''\
from fruit.citrus import lemon, orange, lime
'''
    expected = '''\
from fruit.citrus.lemon import lemon
from fruit.citrus.orange import orange
from fruit.citrus.lime import lime
'''
    self.assertMultiLineEqual( expected, import_expand.expand_text('fruit', text, False, True) )
                      
  def test_expand_text_with_submodule(self):
    text = '''\
from fruit.citrus import lemon, orange, lime
from fruit.color import green, red, yellow
'''
    expected = '''\
from fruit.citrus import lemon
from fruit.citrus import orange
from fruit.citrus import lime
from fruit.color import green, red, yellow
'''
    self.assertMultiLineEqual( expected, import_expand.expand_text('fruit.citrus', text, False, False) )
                      
  def test_expand_text_with_include_module_and_submodule(self):
    text = '''\
from fruit.citrus import lemon, orange, lime
from fruit.color import green, red, yellow
'''
    expected = '''\
from fruit.citrus.lemon import lemon
from fruit.citrus.orange import orange
from fruit.citrus.lime import lime
from fruit.color import green, red, yellow
'''
    self.assertMultiLineEqual( expected, import_expand.expand_text('fruit.citrus', text, False, True) )

  def test_expand_text_with_aliases(self):
    text = '''\
from fruit.citrus import lemon, orange, lime as green_lemon
'''
    expected = '''\
from fruit.citrus import lemon
from fruit.citrus import lime as green_lemon
from fruit.citrus import orange
'''
    self.assertMultiLineEqual( expected, import_expand.expand_text('fruit', text, True, False) )
    
if __name__ == "__main__":
  unit_test.main()

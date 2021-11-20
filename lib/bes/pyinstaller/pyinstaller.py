#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys

from bes.common.check import check
from bes.system.log import logger
from bes.testing.unit_test_class_skip import unit_test_class_skip

class pyinstaller(object):
  'Class to deal with general pyinstaller things.'
  
  log = logger('pyinstaller')

  @classmethod
  def is_binary(clazz):
    'Return True if we are running under a binary frozen by pyinstaller.'
    return clazz.pyinstaller_temp_dir() != None

  @classmethod
  def pyinstaller_temp_dir(clazz):
    'Return the pyinstaller temp frozen stuff unpack dir or None if not frozen.'
    return getattr(sys, '_MEIPASS', None)

  @classmethod
  def raise_skip_if_is_binary(clazz):
    '''
    Raise skip from the setUpClass() method of a unit test fixture
    in order to skip tests that are not meant to run in frozen binary mode
    '''
    if clazz.is_binary():
      unit_test_class_skip.raise_skip('not supported in frozen binary mode.')

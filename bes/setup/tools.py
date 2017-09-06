#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from .unit_test import unit_test
#from bes.common import Shell
#from collections import namedtuple

import subprocess

class tools(unit_test):

  @classmethod
  def find_tests(clazz, d):
    cmd = [ 'find', d, '-name', 'test_*.py' ]
    result = subprocess.check_output(cmd, shell = False)
    return [ x.strip() for x in result.strip().split('\n') if x.strip() ]

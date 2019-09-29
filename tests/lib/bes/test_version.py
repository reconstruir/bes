#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest

class test_version(unittest.TestCase):

  def test_version(self):
    import bes
    print('version=%s; tag=%s; author=%s' % (bes.__version__, bes.__bes_tag__, bes.__author__))
    
if __name__ == "__main__":
  unittest.main()

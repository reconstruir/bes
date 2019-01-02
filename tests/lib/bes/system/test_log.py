#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.system import log

class test_log(unittest.TestCase):

  def test_defaults(self):
    log.configure('foo=debug')
    log.configure('bar=debug')
    log.set_level(log.DEBUG)
    log.reset()
    self.assertEqual( log.DEFAULT_LEVEL, log.get_level() )
    self.assertEqual( log.DEFAULT_LEVEL, log.get_tag_level('foo') )
    self.assertEqual( log.DEFAULT_LEVEL, log.get_tag_level('bar') )

  def test_parse_level(self):
    self.assertEqual( log.CRITICAL, log.parse_level('critical') )
    self.assertEqual( log.DEBUG, log.parse_level('debug') )
    self.assertEqual( log.ERROR, log.parse_level('error') )
    self.assertEqual( log.INFO, log.parse_level('info') )
    self.assertEqual( log.WARNING, log.parse_level('warning') )

    self.assertEqual( log.INFO, log.parse_level('caca') )
    self.assertEqual( log.INFO, log.parse_level('') )
    self.assertEqual( log.INFO, log.INFO )

    self.assertEqual( log.CRITICAL, log.CRITICAL )
    self.assertEqual( log.DEBUG, log.DEBUG )
    self.assertEqual( log.ERROR, log.ERROR )
    self.assertEqual( log.INFO, log.INFO )
    self.assertEqual( log.WARNING, log.WARNING )

  def test_configure(self):
    log.reset()
    log.configure('foo=debug')
    self.assertEqual( log.DEBUG, log.get_tag_level('foo') )
    log.configure('all=info')
    self.assertEqual( log.INFO, log.get_tag_level('foo') )

    self.assertEqual( log.DEFAULT_LEVEL, log.get_level() )
    log.configure('level=critical')
    self.assertEqual( log.INFO, log.get_tag_level('foo') )
    self.assertEqual( log.CRITICAL, log.get_level() )

  def test_add_logging(self):

    class foo(object):

      def __init__(self):
        log.add_logging(self, 'foo')

      def do_stuff(self):
        self.log_e('i did something error')
        self.log_d('i did something debug')
        self.log_i('i did something info')
        self.log_w('i did something warning')
        self.log_c('i did something critical')
        
    f = foo()
    f.do_stuff()

  def test_add_already_has_log_attribute(self):
    class foo(object):
      def __init__(self): log.add_logging(self, 'foo')
      def log(self): pass

    with self.assertRaises(RuntimeError) as context:
      foo()
        
    class bar(object):
      def __init__(self): log.add_logging(self, 'bar')
      log = 666
      
    with self.assertRaises(RuntimeError) as context:
      bar()
      
if __name__ == "__main__":
  unittest.main()

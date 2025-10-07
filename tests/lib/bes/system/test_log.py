#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import multiprocessing, sys
from collections import namedtuple

from bes.system.log import log
from bes.system.log import logger
from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util

class test_log(unit_test):

  def test_default_level(self):
    self.assertEqual( log.DEFAULT_LEVEL, log.get_level() )
  
  def test_set_level(self):
    log.set_level(log.DEBUG)
    self.assertEqual( log.DEBUG, log.get_level() )
    log.reset()

  def xtest_defaults(self):
    log.configure('foo=debug')
    log.configure('bar=debug')
    #log.set_level(log.DEBUG)
    #log.reset()
    self.assertEqual( log.DEFAULT_LEVEL, log.get_level() )
    self.assertEqual( log.DEFAULT_LEVEL, log.get_tag_level('foo') )
    self.assertEqual( log.DEFAULT_LEVEL, log.get_tag_level('bar') )
  
  def test_default_log_level(self):
#    log.configure('foo=debug')
#    log.configure('bar=debug')
#    log.set_level(log.DEBUG)
#    log.reset()
#    self.assertEqual( log.DEFAULT_LEVEL, log.get_level() )
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

  def test_output(self):
    log.output('output to stdout')
      
  @staticmethod
  def _test_log_func_stdout(args):
    l = logger('foo')
    l.configure('format=very_brief')
    l.log_c('critical')
    l.log_d('debug')
    l.log_e('error')
    l.log_i('info')
    l.log_w('warning')
    
  def test_output_stdout(self):
    rv = self.run_test('foo=critical', self._test_log_func_stdout)
    expected = '''\
(foo.CRITICAL)  critical
'''

    self.assert_string_equal( expected, rv.output, native_line_breaks = True )

    rv = self.run_test('foo=debug', self._test_log_func_stdout)
    expected = '''\
(foo.CRITICAL)  critical
(foo.DEBUG)  debug
(foo.ERROR)  error
(foo.INFO)  info
(foo.WARNING)  warning
'''
    self.assert_string_equal( expected, rv.output, native_line_breaks = True )
    
    rv = self.run_test('foo=error', self._test_log_func_stdout)
    expected = '''\
(foo.CRITICAL)  critical
(foo.ERROR)  error
'''
    self.assert_string_equal( expected, rv.output, native_line_breaks = True )

    rv = self.run_test('foo=debug', self._test_log_func_stdout)
    expected = '''\
(foo.CRITICAL)  critical
(foo.DEBUG)  debug
(foo.ERROR)  error
(foo.INFO)  info
(foo.WARNING)  warning
'''
    self.assert_string_equal( expected, rv.output, native_line_breaks = True )

  @staticmethod
  def _test_log_func_stdout_and_output_filename(args):
    inner_tmp_log = args[0]
    l = logger('foo')
    l.configure('format=very_brief')
    l.configure('output=file:{}'.format(inner_tmp_log))
    l.log_c('critical')
    l.log_d('debug')
    l.log_e('error')
    l.log_i('info')
    l.log_w('warning')
    
  def test_both_stdout_and_output_filename(self):
    outer_tmp_log = self.make_temp_file(suffix = '.log')
    rv = self.run_test('foo=critical', self._test_log_func_stdout_and_output_filename, function_args = [ outer_tmp_log ])
    expected = '''\
(foo.CRITICAL)  critical
'''
    self.assert_string_equal( expected, rv.output, native_line_breaks = True )
    self.assert_text_file_equal( expected, outer_tmp_log, codec = 'utf-8', native_line_breaks = True)

    outer_tmp_log = self.make_temp_file(suffix = '.log')
    rv = self.run_test('foo=debug', self._test_log_func_stdout_and_output_filename, function_args = [ outer_tmp_log ])
    expected = '''\
(foo.CRITICAL)  critical
(foo.DEBUG)  debug
(foo.ERROR)  error
(foo.INFO)  info
(foo.WARNING)  warning
'''
    self.assert_string_equal( expected, rv.output, native_line_breaks = True )
    self.assert_text_file_equal( expected, outer_tmp_log, codec = 'utf-8', native_line_breaks = True)
    
    outer_tmp_log = self.make_temp_file(suffix = '.log')
    rv = self.run_test('foo=error', self._test_log_func_stdout_and_output_filename, function_args = [ outer_tmp_log ])
    expected = '''\
(foo.CRITICAL)  critical
(foo.ERROR)  error
'''
    self.assert_string_equal( expected, rv.output, native_line_breaks = True )
    self.assert_text_file_equal( expected, outer_tmp_log, codec = 'utf-8', native_line_breaks = True)

    outer_tmp_log = self.make_temp_file(suffix = '.log')
    rv = self.run_test('foo=debug', self._test_log_func_stdout_and_output_filename, function_args = [ outer_tmp_log ])
    expected = '''\
(foo.CRITICAL)  critical
(foo.DEBUG)  debug
(foo.ERROR)  error
(foo.INFO)  info
(foo.WARNING)  warning
'''
    self.assert_string_equal( expected, rv.output, native_line_breaks = True )
    self.assert_text_file_equal( expected, outer_tmp_log, codec = 'utf-8', native_line_breaks = True)

  @staticmethod
  def _test_log_func_output_filename(args):
    inner_tmp_log = args[0]
    l = logger('foo')
    l.configure('format=very_brief')
    l.configure('output=clear')
    l.configure('output=file:{}'.format(inner_tmp_log))
    l.log_c('critical')
    l.log_d('debug')
    l.log_e('error')
    l.log_i('info')
    l.log_w('warning')
    
  def test_output_filename(self):
      
    outer_tmp_log = self.make_temp_file(suffix = '.log')
    rv = self.run_test('foo=critical', self._test_log_func_output_filename, function_args = [ outer_tmp_log ])
    expected = '''\
(foo.CRITICAL)  critical
'''
    self.assertEqual( '', rv.output )
    self.assert_text_file_equal( expected, outer_tmp_log, codec = 'utf-8', native_line_breaks = True)

    outer_tmp_log = self.make_temp_file(suffix = '.log')
    rv = self.run_test('foo=debug', self._test_log_func_output_filename, function_args = [ outer_tmp_log ])
    expected = '''\
(foo.CRITICAL)  critical
(foo.DEBUG)  debug
(foo.ERROR)  error
(foo.INFO)  info
(foo.WARNING)  warning
'''
    self.assertEqual( '', rv.output )
    self.assert_text_file_equal( expected, outer_tmp_log, codec = 'utf-8', native_line_breaks = True)
    
    outer_tmp_log = self.make_temp_file(suffix = '.log')
    rv = self.run_test('foo=error', self._test_log_func_output_filename, function_args = [ outer_tmp_log ])
    expected = '''\
(foo.CRITICAL)  critical
(foo.ERROR)  error
'''
    self.assertEqual( '', rv.output )
    self.assert_text_file_equal( expected, outer_tmp_log, codec = 'utf-8', native_line_breaks = True)

    outer_tmp_log = self.make_temp_file(suffix = '.log')
    rv = self.run_test('foo=debug', self._test_log_func_output_filename, function_args = [ outer_tmp_log ])
    expected = '''\
(foo.CRITICAL)  critical
(foo.DEBUG)  debug
(foo.ERROR)  error
(foo.INFO)  info
(foo.WARNING)  warning
'''
    self.assertEqual( '', rv.output )
    self.assert_text_file_equal( expected, outer_tmp_log, codec = 'utf-8', native_line_breaks = True)

  #FIXME: broken
  def xtest_all(self):
    def _func(args):
      l = logger('foo')
      l.reset()
      l.configure('format=very_brief')
      l.log_c('critical')
      l.log_d('debug')
      l.log_e('error')
      l.log_i('info')
      l.log_w('warning')
      
    rv = self.run_test('all=debug', _func)
    expected = '''\
(foo.CRITICAL) critical
(foo.DEBUG) debug
(foo.ERROR) error
(foo.INFO) info
(foo.WARNING) warning
'''
    self.assert_string_equal( expected, rv.output, native_line_breaks = True )

  @staticmethod
  def _test_log_func_add_logging(args):
    class foo(object):

      def __init__(self):
        log.add_logging(self, 'foo')
        log.configure('format=very_brief')

      def do_stuff(self):
        self.log_c('critical')
        self.log_d('debug')
        self.log_e('error')
        self.log_i('info')
        self.log_w('warning')
        
    f = foo()
    f.do_stuff()
    
  def test_add_logging(self):
    rv = self.run_test('foo=critical', self._test_log_func_add_logging)
    expected = '''\
(foo.CRITICAL)  critical
'''
    self.assert_string_equal( expected, rv.output, native_line_breaks = True )

    rv = self.run_test('foo=debug', self._test_log_func_add_logging)
    expected = '''\
(foo.CRITICAL)  critical
(foo.DEBUG)  debug
(foo.ERROR)  error
(foo.INFO)  info
(foo.WARNING)  warning
'''
    self.assert_string_equal( expected, rv.output, native_line_breaks = True )
    
    rv = self.run_test('foo=error', self._test_log_func_add_logging)
    expected = '''\
(foo.CRITICAL)  critical
(foo.ERROR)  error
'''
    self.assert_string_equal( expected, rv.output, native_line_breaks = True )

    rv = self.run_test('foo=debug', self._test_log_func_add_logging)
    expected = '''\
(foo.CRITICAL)  critical
(foo.DEBUG)  debug
(foo.ERROR)  error
(foo.INFO)  info
(foo.WARNING)  warning
'''
    self.assert_string_equal( expected, rv.output, native_line_breaks = True )

  class _log_tester(multiprocessing.Process):

    def __init__(self, function, config, output_filename, function_args):
      super(test_log._log_tester, self).__init__()
      self._function = function
      self._function_args = function_args
      self._config = config
      self._output_filename = output_filename
  
    def run(self):
      sys.stdout = open(self._output_filename, 'w') #, buffering = 0)
      log.configure(self._config)
      self._function(self._function_args)
      sys.stdout.flush()
      return 0
    
  _test_result = namedtuple('_test_result', 'output_filename, output')
  def run_test(self, config, function, function_args = None):
    tmp_output_filename = self.make_temp_file(suffix = '.output')
    p = self._log_tester(function, config, tmp_output_filename, function_args)
    p.start()
    p.join()
    output = file_util.read(tmp_output_filename, codec = 'utf-8')
    return self._test_result(tmp_output_filename, output)
    
if __name__ == '__main__':
  unit_test.main()

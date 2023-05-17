#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import Queue as py_queue

from bes.testing.unit_test import unit_test
from bes.btask.btask_main_thread_runner_py import btask_main_thread_runner_py

class test_btask_main_thread_runner_py(unit_test):

  def test_call_in_main_thread(self):
    runner = btask_main_thread_runner()

    q = py_queue()
    
    def kiwi(*args, **kwargs):
      q.put( { 'name': 'kiwi', 'args': args, 'kwargs': kwargs } )

    def lemon(*args, **kwargs):
      q.put( { 'name': 'lemon', 'args': args, 'kwargs': kwargs } )

    def spawn(function, *args, **kwargs):
      def _thread_main(
      q.put( { 'name': 'lemon', 'args': args, 'kwargs': kwargs } )
      
      
    runner.call_in_main_thread(kiwi, 1, color = 'green')
    runner.call_in_main_thread(kiwi, 2, color = 'yellow')

    runner.call_in_main_thread(lemon, 1, color = 'green')
    runner.call_in_main_thread(lemon, 2, color = 'yellow')

    
    text = '''\
BES_VERSION = u'1.0.0'
BES_AUTHOR_NAME = u'Sally Foo'
BES_AUTHOR_EMAIL = u'sally@foo.com'
BES_ADDRESS = u''
BES_TAG = u''
BES_TIMESTAMP = u''
'''
    self.assertEqual( (u'1.0.0', u'Sally Foo', u'sally@foo.com', u'', u'', u''), version_info.read_string(text) )
    
  def test___str__(self):
    expected = '''\
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

BES_VERSION = u'1.0'
BES_AUTHOR_NAME = u'Sally Bar'
BES_AUTHOR_EMAIL = u'sally@bar.com'
BES_ADDRESS = u''
BES_TAG = u''
BES_TIMESTAMP = u''
'''
    self.assertMultiLineEqual( expected, str(version_info(u'1.0', u'Sally Bar', u'sally@bar.com', u'', u'', u'')) )
    
  def test_change(self):
    vi = version_info(u'1.0', u'Sally Bar', u'sally@bar.com', u'', u'', u'')
    self.assertEqual( (u'1.0', u'Sally Bar', u'sally@bar.com', u'', u'666', u'123'), vi.change(tag = u'666', timestamp = u'123') )
    
  def test_version_string(self):
    self.assertEqual(u'1.0:foo@bar:123:abc', version_info(u'1.0', u'Sally Bar', u'sally@bar.com', u'foo@bar', u'123', u'abc').version_string() )
    
if __name__ == '__main__':
  unit_test.main()

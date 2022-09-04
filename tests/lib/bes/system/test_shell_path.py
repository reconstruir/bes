#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.system.shell_path import shell_path

class test_shell_path(unit_test):

  def test_split(self):
    self.assertEqual( [], shell_path.split(None) )
    self.assertEqual( [], shell_path.split('') )
    self.assertEqual( [ 'a', 'b' ], shell_path.split(self.native_path('a:b')) )
    self.assertEqual( [ 'a' ], shell_path.split(self.native_path('a')) )
    self.assertEqual( [ 'a', 'b', 'a' ], shell_path.split(self.native_path('a:b:a')) )

  def test_join(self):
    self.assertEqual( self.native_path('a:b'), shell_path.join([ 'a', 'b' ] ) )
    self.assertEqual( self.native_path('a'), shell_path.join([ 'a' ]) )
    self.assertEqual( self.native_path('a:b:a'), shell_path.join([ 'a', 'b', 'a' ]) )
    
  def test_remove_duplicates(self):
    self.assertEqual( self.native_path(''), shell_path.remove_duplicates('') )
    self.assertEqual( self.native_path('a:b'), shell_path.remove_duplicates('a:b') )
    self.assertEqual( self.native_path('a'), shell_path.remove_duplicates('a') )
    self.assertEqual( self.native_path('a:b'), shell_path.remove_duplicates(self.native_path('a:b:a')) )

  def test_normalize(self):
    self.assertEqual( self.native_path(''), shell_path.normalize('') )
    self.assertEqual( self.native_path('/usr/bin'), shell_path.normalize('/usr/bin/') )
    self.assertEqual( self.native_path('/usr/bin'), shell_path.normalize('/usr/bin//') )
    self.assertEqual( self.native_path('/usr/bin'), shell_path.normalize('/usr//bin') )
    self.assertEqual( self.native_path('/usr/bin'), shell_path.normalize('//usr/bin') )
    self.assertEqual( self.native_path('/usr/bin'), shell_path.normalize('///usr/bin') )
    self.assertEqual( self.native_path('/usr/bin'), shell_path.normalize('///usr///bin///') )
    self.assertEqual( self.native_path('/usr/bin:/bin'), shell_path.normalize('/usr/bin::/bin') )
    self.assertEqual( self.native_path('/usr/bin:/bin'), shell_path.normalize('://usr/bin/::/bin//:') )
    self.assertEqual( self.native_path(''), shell_path.normalize(':') )
    #self.assertEqual( self.native_path('a:b'), shell_path.normalize('a:b') )
    #self.assertEqual( self.native_path('a'), shell_path.normalize('a') )
    #self.assertEqual( self.native_path('a:b'), shell_path.normalize(self.native_path('a:b:a')) )
    
  def test_diff(self):
    self.assertEqual( ( [], [], [] ), self._call_diff('/usr/bin:/bin', '/usr/bin:/bin') )
    self.assertEqual( ( [ '/kiwi/bin' ], [], [ '/bin' ] ), self._call_diff('/usr/bin:/bin', '/usr/bin:/kiwi/bin') )
    
  def xtest_diff_prepend(self):
    self.assertEqual( ( [], [ '/kiwi/bin' ], [ '/bin' ] ), self._call_diff('/usr/bin:/bin', '/kiwi/bin:/usr/bin') )

  def test_resolve(self):
    self.assertEqual( self.native_path(''), shell_path.resolve('') )
    self.assertEqual( self.native_path('/usr/bin:/bin'), shell_path.resolve('/usr/bin:/bin') )
    self.assertEqual( self.native_path('/usr/bin:/bin'), shell_path.resolve([ '/usr/bin', '/bin' ]) )
    self.assertEqual( self.native_path('/usr/bin:/bin'), shell_path.resolve(( '/usr/bin', '/bin' )) )

    with self.assertRaises(TypeError) as _:
      shell_path.resolve(( '/usr/bin', [ '/bin' ] ))

  def _call_remove(self, p1, p2):
    return shell_path.remove(self.native_path(p1), self.native_path(p2))
      
  def test_remove(self):
    self.assertEqual( '', self._call_remove('', 'foo') )
    self.assertEqual( '/usr/bin', self._call_remove('/usr/bin:/bin', '/bin') )
    self.assertEqual( '', self._call_remove('/usr/bin:/bin', '/usr/bin:/bin') )
    self.assertEqual( '', self._call_remove('/usr/bin:/bin', '/bin:/usr/bin') )
    self.assertEqual( '', self._call_remove('/usr/bin:/bin', '/bin:/usr/bin:') )
    self.assertEqual( '', self._call_remove('/usr/bin:/bin', '/bin:/usr/bin:/bin') )
    self.assertEqual( '/usr/bin:/usr/bin', self._call_remove('/usr/bin:/usr/bin', '/bin') )
    self.assertEqual( '', self._call_remove('/usr/bin:/bin:/usr/bin', '/bin:/usr/bin') )

  def _call_append(self, p1, p2):
    return shell_path.append(self.native_path(p1), self.native_path(p2))
      
  def test_append(self):
    self.assertEqual( '/bin', self._call_append('', '/bin') )
    self.assertEqual( '/bin:/usr/bin', self._call_append('/bin', '/usr/bin') )
    self.assertEqual( '/bin:/usr/bin', self._call_append('/bin:/usr/bin', '/usr/bin') )
    self.assertEqual( '/bin:/usr/bin', self._call_append('/usr/bin:/bin', '/usr/bin') )

  def _call_prepend(self, p1, p2):
    return shell_path.prepend(self.native_path(p1), self.native_path(p2))
      
  def test_prepend(self):
    self.assertEqual( '/bin', self._call_prepend('', '/bin') )
    self.assertEqual( '/usr/bin:/bin', self._call_prepend('/bin', '/usr/bin') )
    self.assertEqual( '/usr/bin:/bin', self._call_prepend('/bin:/usr/bin', '/usr/bin') )
    self.assertEqual( '/usr/bin:/bin', self._call_prepend('/usr/bin:/bin', '/usr/bin') )
    
  def xtest_diff_p1_in_p2(self):
    self.assertEqual( (
      [ '/lemon/bin' ],
      [ '/kiwi/bin' ],
      [],
    ), self._call_diff('/bin:/usr/bin', '/kiwi/bin:/bin:/usr/bin:/lemon/bin') )

    self.assertEqual( (
      [ '/lemon/bin' ],
      [ '/kiwi/bin' ],
      [],
    ), self._call_diff('/bin:/usr/bin:/bin', '/kiwi/bin:/bin:/usr/bin:/bin:/lemon/bin') )
    
  def _call_diff(self, p1, p2):
    return shell_path.diff(self.native_path(p1), self.native_path(p2))
    
if __name__ == '__main__':
  unit_test.main()

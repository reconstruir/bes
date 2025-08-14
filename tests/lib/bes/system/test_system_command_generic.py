#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.host import host
from bes.system.system_command_generic import system_command_generic
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip
from bes.files.bf_file_ops import bf_file_ops

class test_system_command_generic(unit_test):

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix(self):
    tmp_dir = self._make_test_dir()
    cmd = system_command_generic('ls')
    rv = cmd.call_command([ '-1', tmp_dir])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( b'a.txt\nb.txt\nc.txt\n', rv.stdout_bytes )

  @unit_test_function_skip.skip_if(not host.is_macos(), 'not macos')
  def test_macos(self):
    tmp_dir = self._make_test_dir()
    cmd = system_command_generic('dscl')
    rv = cmd.call_command([ '.', '-read', '/Groups/wheel', 'PrimaryGroupID' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( b'PrimaryGroupID: 0\n', rv.stdout_bytes )
  
  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows(self):
    pass

  def _make_test_dir(self):
    tmp_dir = self.make_temp_dir()
    bf_file_ops.save(path.join(tmp_dir, 'a.txt'), content = 'this is a')
    bf_file_ops.save(path.join(tmp_dir, 'b.txt'), content = 'this is b')
    bf_file_ops.save(path.join(tmp_dir, 'c.txt'), content = 'this is c')
    return tmp_dir
  
if __name__ == '__main__':
  unit_test.main()

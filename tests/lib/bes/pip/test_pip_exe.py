#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_util import file_util
from bes.pip.pip_exe import pip_exe
from bes.system.host import host
from bes.testing.unit_test import unit_test

class test_pip_exe(unit_test):

  def test_version_info(self):
    fake_exe = self._make_temp_fake_pip('pip', 'pip', '2.7', '666.0.1')
    self.assertEqual( ( '666.0.1', '/foo/site-packages/pip', '2.7' ), pip_exe.version_info(fake_exe) )

  def test_version(self):
    fake_exe = self._make_temp_fake_pip('pip', 'pip', '2.7', '666.0.1')
    self.assertEqual( '666.0.1', pip_exe.version(fake_exe) )
    
  def _make_temp_fake_pip(self, filename, name, python_version, version, mode = 0o0755):
    if host.is_unix():
      return self._make_temp_fake_pip_unix(filename, name, python_version, version, mode = mode)
    elif host.is_windows():
      return self._make_temp_fake_pip_windows(filename, name, python_version, version, mode = mode)
    else:
      host.raise_unsupported_system()

  def _make_temp_fake_pip_unix(self, filename, name, python_version, version, mode = 0o0755):
    tmp_dir = self.make_temp_dir()
    tmp_exe = path.join(tmp_dir, filename)
    content = '''\
#!/bin/bash
echo "{name} {version} from /foo/site-packages/pip (python {python_version})"
exit 0
'''.format(name = name, python_version = python_version, version = version)
    file_util.save(tmp_exe, content = content, mode = mode)
    return tmp_exe

  def _make_temp_fake_pip_windows(self, filename, name, python_version, version, mode = 0o0755):
    tmp_dir = self.make_temp_dir()
    assert not filename.endswith('.bat')
    filename = filename + '.bat'
    tmp_exe = path.join(tmp_dir, filename)
    content = '''\
@echo off
echo {name} {version} from /foo/site-packages/pip (python {python_version})
exit /b 0
'''.format(name = name, python_version = python_version, version = version)
    file_util.save(tmp_exe, content = content, mode = mode)
    return tmp_exe
  
if __name__ == '__main__':
  unit_test.main()

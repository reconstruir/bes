#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_util import file_util
from bes.pipenv.pipenv_exe import pipenv_exe
from bes.system.host import host
from bes.testing.unit_test import unit_test

class test_pipemv_exe(unit_test):

  def test_version(self):
    fake_exe = self._make_temp_fake_pipenv('pipenv', '2020.1.13')
    self.assertEqual( '2020.1.13', pipenv_exe.version(fake_exe) )
    
  def _make_temp_fake_pipenv(self, filename, version, mode = 0o0755, make_site_package_dir = False):
    if host.is_unix():
      fake_pipenv = self._make_temp_fake_pipenv_unix(filename,
                                                  version,
                                                  mode = mode)
    elif host.is_windows():
      fake_pipenv = self._make_temp_fake_pipenv_windows(filename,
                                                  version,
                                                  mode = mode)
    else:
      host.raise_unsupported_system()
    return fake_pipenv

  def _make_temp_fake_pipenv_unix(self, filename, version, mode = 0o0755):
    tmp_dir = self.make_temp_dir()
    tmp_exe = path.join(tmp_dir, 'bin', filename)
    content = '''\
#!/bin/bash
echo "pipenv, version {version}"
exit 0
'''.format(version = version)
    file_util.save(tmp_exe, content = content, mode = mode)
    return tmp_exe

  def _make_temp_fake_pipenv_windows(self, filename, version, mode = 0o0755):
    tmp_dir = self.make_temp_dir()
    assert not filename.endswith('.bat')
    filename = filename + '.bat'
    tmp_exe = path.join(tmp_dir, 'bin', filename)
    content = '''\
@echo off
echo "pipenv, version {version}"
exit /b 0
'''.format(version = version)
    file_util.save(tmp_exe, content = content, mode = mode)
    return tmp_exe
  
if __name__ == '__main__':
  unit_test.main()

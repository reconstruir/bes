#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_util import file_util
from bes.pip.pip_exe import pip_exe
from bes.system.host import host
from bes.testing.unit_test import unit_test

class test_pip_exe(unit_test):

  def test_filename_info_no_version(self):
    fake_exe, _ = self._make_temp_fake_pip('pip', 'pip', '2.7', '666.0.1')
    self.assertEqual( ( None, None ), pip_exe.filename_info(fake_exe) )
  
  def test_filename_info_major_version(self):
    fake_exe, _ = self._make_temp_fake_pip('pip2', 'pip', '2.7', '666.0.1')
    self.assertEqual( ( '2', None ), pip_exe.filename_info(fake_exe) )
  
  def test_filename_info_major_and_minor_version(self):
    fake_exe, _ = self._make_temp_fake_pip('pip2.7', 'pip', '2.7', '666.0.1')
    self.assertEqual( ( '2.7', None ), pip_exe.filename_info(fake_exe) )

  def test_filename_info_no_version_with_site_packages(self):
    fake_exe, lib_dir = self._make_temp_fake_pip('pip', 'pip', '2.7', '666.0.1', make_site_package_dir = True)
    self.assertEqual( ( None, lib_dir ), pip_exe.filename_info(fake_exe) )

  def test_filename_info_major_version_with_site_packages(self):
    fake_exe, lib_dir = self._make_temp_fake_pip('pip2', 'pip', '2.7', '666.0.1', make_site_package_dir = True)
    self.assertEqual( ( '2', lib_dir ), pip_exe.filename_info(fake_exe) )
    
  def test_version_info(self):
    fake_exe, _ = self._make_temp_fake_pip('pip', 'pip', '2.7', '666.0.1')
    self.assertEqual( ( '666.0.1', '/foo/site-packages/pip', '2.7' ), pip_exe.version_info(fake_exe) )

  def test_version(self):
    fake_exe, _ = self._make_temp_fake_pip('pip', 'pip', '2.7', '666.0.1')
    self.assertEqual( '666.0.1', pip_exe.version(fake_exe) )
    
  def _make_temp_fake_pip(self, filename, name, python_version, version, mode = 0o0755, make_site_package_dir = False):
    if host.is_unix():
      fake_pip = self._make_temp_fake_pip_unix(filename,
                                               name,
                                               python_version,
                                               version,
                                               mode = mode)
    elif host.is_windows():
      fake_pip = self._make_temp_fake_pip_windows(filename,
                                                  name,
                                                  python_version,
                                                  version,
                                                  mode = mode)
    else:
      host.raise_unsupported_system()
    if make_site_package_dir:
      lib_dir = path.normpath(path.join(path.dirname(fake_pip), path.pardir, 'lib', 'python', 'site-packages'))
      file_util.mkdir(lib_dir)
    else:
      lib_dir = None
    return fake_pip, lib_dir

  def _make_temp_fake_pip_unix(self, filename, name, python_version, version, mode = 0o0755):
    tmp_dir = self.make_temp_dir()
    tmp_exe = path.join(tmp_dir, 'bin', filename)
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
    tmp_exe = path.join(tmp_dir, 'bin', filename)
    content = '''\
@echo off
echo {name} {version} from /foo/site-packages/pip (python {python_version})
exit /b 0
'''.format(name = name, python_version = python_version, version = version)
    file_util.save(tmp_exe, content = content, mode = mode)
    return tmp_exe
  
if __name__ == '__main__':
  unit_test.main()

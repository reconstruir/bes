#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from ..system.check import check
from ..fs.file_util import file_util
from ..fs.temp_file import temp_file
from ..system.host import host
from ..system.log import logger
from ..version.semantic_version import semantic_version
from ..property.cached_property import cached_property
from ..testing.unit_test_function_skip import unit_test_function_skip

from .python_discovery import python_discovery
from .python_error import python_error
from .python_exe import python_exe
from .python_version import python_version

class python_testing(object):
  'Class to deal with the python testing.'

  _log = logger('python_testing')

  class _python_constants(object):

    @cached_property
    def PYTHON_38(self):
      return python_discovery.find_by_version('3.8')

    @cached_property
    def PYTHON_39(self):
      return python_discovery.find_by_version('3.9')

    @cached_property
    def PYTHON_310(self):
      return python_discovery.find_by_version('3.10')

    @cached_property
    def PYTHON_311(self):
      return python_discovery.find_by_version('3.11')

    @cached_property
    def PYTHON_312(self):
      return python_discovery.find_by_version('3.12')

    @cached_property
    def PYTHON_313(self):
      return python_discovery.find_by_version('3.13')
    
    @cached_property
    def ALL_PYTHONS(self):
      return python_discovery.all_exes()
    
    @cached_property
    def ANY_PYTHON(self):
      return python_discovery.any_exe()
    
    @cached_property
    def ANY_PYTHON2(self):
      return python_discovery.find_by_major_version(2)
    
    @cached_property
    def ANY_PYTHON3(self):
      return python_discovery.find_by_major_version(3)

  _PYTHONS = _python_constants()
  if False:
    _log.log_d('  PYTHON_38: {}'.format(_PYTHONS.PYTHON_38))
    _log.log_d('  PYTHON_39: {}'.format(_PYTHONS.PYTHON_39))
    _log.log_d(' PYTHON_310: {}'.format(_PYTHONS.PYTHON_310))
    _log.log_d(' PYTHON_311: {}'.format(_PYTHONS.PYTHON_311))
    _log.log_d(' PYTHON_312: {}'.format(_PYTHONS.PYTHON_312))
    _log.log_d(' PYTHON_313: {}'.format(_PYTHONS.PYTHON_313))
    _log.log_d('ALL_PYTHONS: {}'.format(' '.join(_PYTHONS.ALL_PYTHONS)))
    _log.log_d(' ANY_PYTHON: {}'.format(_PYTHONS.ANY_PYTHON))
    _log.log_d('ANY_PYTHON2: {}'.format(_PYTHONS.ANY_PYTHON2))
    _log.log_d('ANY_PYTHON3: {}'.format(_PYTHONS.ANY_PYTHON3))

  PYTHON_VERSIONS = ( '3.8', '3.9', '3.10', '3.11', '3.12', '3.13' )
  @classmethod
  def make_fake_python_installation(clazz, root_dir, py_version, pip_version,
                                    source, system = None):
    check.check_string(root_dir)
    check.check_string(py_version)
    check.check_string(pip_version, allow_none = True)
    check.check_string(source, allow_none = True)
    check.check_string(system, allow_none = True)

    if not py_version in clazz.PYTHON_VERSIONS:
      raise python_error('unsupported python version: "{}"'.format(py_version))
    system = system or host.SYSTEM
    
    if system == host.MACOS:
      clazz._make_fake_python_installation_macos(root_dir,
                                                 py_version,
                                                 pip_version,
                                                 source)
    elif system == host.LINUX:
      clazz._make_fake_python_installation_linux(root_dir,
                                                 py_version,
                                                 pip_version,
                                                 source)
    elif system == host.WINDOWS:
      clazz._make_fake_python_installation_windows(root_dir,
                                                   py_version,
                                                   pip_version,
                                                   source)
    else:
      host.raise_unsupported_system()

  @classmethod
  def make_temp_fake_python_installation(clazz, py_version, pip_version, source,
                                         system = None, debug = False):
    tmp_dir = temp_file.make_temp_dir(delete = not debug)
    clazz.make_fake_python_installation(tmp_dir, py_version, pip_version, source)
    return tmp_dir

  @classmethod
  def _make_fake_python_installation_macos(clazz, root_dir, py_version, pip_version, source):
    if source == 'xcode':
      return clazz._make_fake_python_installation_macos_xcode(root_dir, py_version, pip_version)
    elif source == 'brew':
      return clazz._make_fake_python_installation_macos_brew(root_dir, py_version, pip_version)
    elif source == 'system':
      return clazz._make_fake_python_installation_macos_system(root_dir, py_version, pip_version)
    else:
      raise python_error('unknown python source: "{}"'.format(source))

  @classmethod
  def _make_fake_python_installation_macos_brew(clazz, root_dir, py_version, pip_version):
    python_major_version = python_version(py_version).major
    bin_dir = path.join(root_dir, 'bin')
    fake_python = path.join(bin_dir, 'python')
    fake_python_with_version = path.join(bin_dir, 'python{}'.format(py_version))
    fake_python_major_version = path.join(bin_dir, 'python{}'.format(python_major_version))
    fake_pip = path.join(bin_dir, 'pip')
    fake_pip_with_version = path.join(bin_dir, 'pip{}'.format(py_version))
    fake_pip_major_version = path.join(bin_dir, 'pip{}'.format(python_major_version))

    clazz._make_fake_python_unix(fake_python, py_version)
    clazz._make_fake_python_unix(fake_python_with_version, py_version)
    clazz._make_fake_python_unix(fake_python_major_version, py_version)

    clazz._make_fake_pip_unix(fake_pip, pip_version, py_version)
    clazz._make_fake_pip_unix(fake_pip_with_version, pip_version, py_version)
    clazz._make_fake_pip_unix(fake_pip_major_version, pip_version, py_version)
    
  @classmethod
  def _make_fake_python_installation_macos_xcode(clazz, root_dir, py_version, pip_version):
    python_major_version = python_version(py_version).major
    bin_dir = path.join(root_dir, 'bin')
    fake_python_major_version = path.join(bin_dir, 'python{}'.format(python_major_version))
    fake_pip_major_version = path.join(bin_dir, 'pip{}'.format(python_major_version))
    clazz._make_fake_python_unix(fake_python_major_version, py_version)
    clazz._make_fake_pip_unix(fake_pip_major_version, pip_version, py_version)

  @classmethod
  def _make_fake_python_installation_macos_system(clazz, root_dir, py_version, pip_version):
    assert py_version == '2.7'
    python_major_version = python_version(py_version).major
    bin_dir = path.join(root_dir, 'bin')
    fake_python = path.join(bin_dir, 'python')
    fake_python_with_major_version = path.join(bin_dir, 'python2')
    fake_python_with_version = path.join(bin_dir, 'python2.7')
    clazz._make_fake_python_unix(fake_python, py_version)
    clazz._make_fake_python_unix(fake_python_with_major_version, py_version)
    clazz._make_fake_python_unix(fake_python_with_version, py_version)
    
  @classmethod
  def _make_fake_python_installation_linux(clazz, root_dir, py_version, pip_version, source):
    assert False

  @classmethod
  def _make_fake_python_installation_windows(clazz, root_dir, py_version, pip_version, source):
    python_major_version = python_version(py_version).major
    fake_python = path.join(root_dir, 'python.bat')
    fake_python_with_version = path.join(root_dir, 'python{}.bat'.format(py_version))
    fake_python_major_version = path.join(root_dir, 'python{}.bat'.format(python_major_version))
    fake_pip = path.join(root_dir, 'Scripts', 'pip.bat')
    fake_pip_with_version = path.join(root_dir, 'Scripts', 'pip{}.bat'.format(py_version))
    fake_pip_major_version = path.join(root_dir, 'Scripts', 'pip{}.bat'.format(python_major_version))
    fake_pip_no_version = path.join(root_dir, 'Scripts', 'pip.bat')

    clazz._make_fake_python_windows(fake_python, py_version)
    clazz._make_fake_python_windows(fake_python_with_version, py_version)
    clazz._make_fake_python_windows(fake_python_major_version, py_version)

    clazz._make_fake_pip_windows(fake_pip, pip_version, py_version)
    clazz._make_fake_pip_windows(fake_pip_with_version, pip_version, py_version)
    clazz._make_fake_pip_windows(fake_pip_major_version, pip_version, py_version)
    clazz._make_fake_pip_windows(fake_pip_no_version, pip_version, py_version)

  @classmethod
  def _make_fake_python_unix(clazz, filename, version):
    # python <= 2.7 outputs the version to stderr
    content2 = f'''\
#!/bin/bash
echo Python {version} 1>&2
exit 0
'''
    # python >= 3.0 outputs the version to stdout
    content3 = f'''\
#!/bin/bash
echo Python {version}
exit 0
'''
    content = content2 if semantic_version(version) < '3.0' else content3
    return file_util.save(filename, content = content)

  @classmethod
  def _make_fake_python_windows(clazz, filename, version):
    content = '''\
@echo off
echo Python {version}
exit /b 0
'''.format(version = version)
    return file_util.save(filename, content = content, mode = 0o0755)
      
  @classmethod
  def make_fake_python(clazz, filename, version):
    if host.is_unix():
      return clazz._make_fake_python_unix(filename, version)
    elif host.is_windows():
      assert file_util.extension(filename) not in ( 'bat', 'exe', 'cmd', 'ps1' )
      return clazz._make_fake_python_windows(filename + '.cmd', version)
    else:
      host.raise_unsupported_system()
      
  @classmethod
  def make_temp_fake_python(clazz, filename, version, mode = None, debug = False):
    tmp_dir = temp_file.make_temp_dir(delete = not debug)
    path.join(tmp_dir, filename)
    tmp_exe = clazz.make_fake_python(path.join(tmp_dir, filename), version)
    if mode:
      os.chmod(tmp_exe, mode)
    return tmp_exe
      
  @classmethod
  def _make_fake_python_unix(clazz, filename, version):
    content = '''\
#!/bin/bash
echo Python {version} 1>&2
exit 0
'''.format(version = version)
    return file_util.save(filename, content = content, mode = 0o0755)

  @classmethod
  def _make_fake_python_windows(clazz, filename, version):
    content = '''\
@echo off
echo Python {version}
exit /b 0
'''.format(version = version)
    return file_util.save(filename, content = content, mode = 0o0755)

  @classmethod
  def make_fake_pip(clazz, filename, version, py_version):
    if host.is_unix():
      return clazz._make_fake_pip_unix(filename, version, py_version)
    elif host.is_windows():
      assert file_util.extension(filename) not in ( 'bat', 'exe', 'cmd', 'ps1' )
      return clazz._make_fake_pip_windows(filename + '.cmd', version, py_version)
    else:
      host.raise_unsupported_system()

  @classmethod
  def make_temp_fake_pip(clazz, filename, version, py_version, mode = None, debug = False):
    mode = mode or 0o0755

    tmp_dir = temp_file.make_temp_dir(delete = not debug)
    tmp_exe = clazz.make_fake_pip(path.join(tmp_dir, filename), version, py_version)
    if mode:
      os.chmod(tmp_exe, mode)
    return tmp_exe
      
  @classmethod
  def _make_fake_pip_unix(clazz, filename, pip_version, py_version):
    content = '''\
#!/bin/bash
echo "pip {pip_version} from /foo/site-packages/pip (python {py_version})"
exit 0
'''.format(py_version = py_version, pip_version = pip_version)
    return file_util.save(filename, content = content, mode = 0o0755)

  @classmethod
  def _make_fake_pip_windows(clazz, filename, pip_version, py_version):
    content = '''\
@echo off
echo pip {pip_version} from /foo/site-packages/pip (python {py_version})
exit /b 0
'''.format(py_version = py_version, pip_version = pip_version)
    return file_util.save(filename, content = content, mode = 0o0755)

  @staticmethod
  def skip_if_not(name, is_system, exe, version):
    not_system = not getattr(host, is_system)()
    not_found = not exe
    parts = []
    if not_system:
      parts.append(f'not "{is_system}"')
    if not_found:
      parts.append(f'"python {version}" not found')
    message_right = ' and '.join(parts)
    message = f'{name}: {message_right}'
    return unit_test_function_skip.skip_if(not_system or not_found,
                                           message,
                                           warning = True)
  

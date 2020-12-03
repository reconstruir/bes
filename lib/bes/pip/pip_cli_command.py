#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import sys

from bes.common.check import check
from bes.common.Script import Script
from bes.script.blurber import blurber

from .pip_error import pip_error
from .pip_exe import pip_exe
from .pip_installer import pip_installer

class pip_cli_command(object):
  'python cli commands.'

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(pip_cli_command, command)
    return func(**kargs)

  @classmethod
  def ver(clazz, py_exe):
    check.check_string(py_exe)
    
    exe = pip_exe.pip_exe(py_exe)
    print(pip_exe.version(exe))
    return 0

  @classmethod
  def info(clazz, py_exe):
    check.check_string(py_exe)

    exe = pip_exe.pip_exe(py_exe)
    print(pip_exe.version_info(exe))
    return 0

  @classmethod
  def present(clazz, py_exe, verbose):
    check.check_string(py_exe)
    check.check_bool(verbose)

    installer = clazz._make_installer(verbose)
    exe = pip_exe.pip_exe(py_exe)
    if pip_exe.pip_exe_is_valid(exe):
      return 0
    else:
      return 1

  @classmethod
  def update(clazz, py_exe, pip_version, verbose):
    check.check_string(py_exe)
    check.check_string(pip_version)
    check.check_bool(verbose)

    installer = clazz._make_installer(verbose)
    installer.update(py_exe, pip_version)
    return 0

  @classmethod
  def uninstall(clazz, py_exe, verbose):
    check.check_string(py_exe)
    check.check_bool(verbose)

    installer = clazz._make_installer(verbose)
    installer.uninstall(py_exe)
    return 0
  
  @classmethod
  def _make_installer(clazz, verbose):
    bl = blurber(Script.name())
    bl.set_verbose(verbose)
    return pip_installer(bl)

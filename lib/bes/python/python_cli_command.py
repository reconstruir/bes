#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys

from bes.common.check import check
from bes.common.Script import Script
from bes.script.blurber import blurber
from bes.script.blurber import blurber
from bes.text.text_box import text_box_unicode, text_box_space
from bes.text.text_table import text_table, text_cell_renderer, text_table_style

from .python_installer import python_installer
from .python_exe import python_exe

class python_cli_command(object):
  'python cli commands.'

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(python_cli_command, command)
    return func(**kargs)

  @classmethod
  def ver(clazz):
    print(sys.version)
    return 0

  @classmethod
  def path(clazz):
    for p in sys.path:
      print(p)
    return 0

  @classmethod
  def available(clazz, num, verbose):
    check.check_int(num)

    installer = clazz._make_installer(verbose)
    available = installer.available_versions(num)
    for full_version in available:
      print(full_version)
    return 0
  
  @classmethod
  def install(clazz, full_version, verbose):
    check.check_string(full_version)

    installer = clazz._make_installer(verbose)
    installer.install(full_version)
    
    return 0

  @classmethod
  def uninstall(clazz, full_version, verbose):
    check.check_string(full_version)

    installer = clazz._make_installer(verbose)
    installer.uninstall(full_version)
    
    return 0

  @classmethod
  def installed(clazz, verbose):
    installer = clazz._make_installer(verbose)
    installed = installer.installed_versions()
    for full_version in installed:
      print(full_version)
    return 0
  
  @classmethod
  def reinstall(clazz, full_version, verbose):
    check.check_string(full_version)

    installer = clazz._make_installer(verbose)
    installer.uninstall(full_version)
    installer.install(full_version)
    return 0

  @classmethod
  def _make_installer(clazz, verbose):
    bl = blurber(Script.name())
    bl.set_verbose(verbose)
    return python_installer(bl)
  
  @classmethod
  def info(clazz, exe):
    python_exe.check_exe(exe)

    info = python_exe.info(exe)
    tt = text_table(data = zip(tuple(info._fields), info))
    print(tt)
    return 0

  @classmethod
  def exes(clazz, show_info):
    check.check_bool(show_info)
    
    python_exes = python_exe.find_python_exes()
    for exe in python_exes:
      print(exe)
      if show_info:
        clazz.info(exe)
    return 0
  

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# Borrowed from: http://stackoverflow.com/questions/21936292/conditional-skip-testcase-decorator-in-nosetests

import unittest, sys
from bes.system.host import host

class unit_test_class_skip(object):

  @classmethod
  def raise_skip(clazz, message):
    raise unittest.SkipTest(message)

  def raise_skip_if(conditional, message):
    if not conditional:
      raise unittest.SkipTest(message)
  
  @classmethod
  def raise_skip_if_not(clazz, conditional, message):
    if not conditional:
      clazz.raise_skip(message)

  @classmethod
  def raise_skip_if_not_platform(clazz, system):
    clazz.raise_skip_if_not(system == host.SYSTEM, 'system is not {}: {}'.format(system, host.SYSTEM))

  @classmethod
  def raise_skip_if_not_unix(clazz):
    clazz.raise_skip_if_not(host.is_unix(), 'system is not unix: {}'.format(host.SYSTEM))

  @classmethod
  def raise_skip_if_not_windows(clazz):
    clazz.raise_skip_if_not_platform(host.WINDOWS)

  @classmethod
  def raise_skip_if_not_macos(clazz):
    clazz.raise_skip_if_not_platform(host.MACOS)
  
  @classmethod
  def raise_skip_if_not_linux(clazz):
    clazz.raise_skip_if_not_platform(host.LINUX)

  @classmethod
  def raise_skip_if_not_python_version_matches(clazz, major, minor, message):
    if sys.version_info.major == major and sys.version_info.minor == minor:
      clazz.raise_skip(message)

  @classmethod
  def raise_skip_if_not_python_major_version_matches(clazz, major, message):
    if sys.version_info.major == major:
      clazz.raise_skip(message)

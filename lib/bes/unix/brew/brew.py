#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.host import host

from .brew_error import brew_error

class brew(object):
  'Class to deal with brew on macos.'

  @classmethod
  def has_brew(clazz):
    'Return True if brew is installed.'

    clazz._check_macos()

  @classmethod
  def install(clazz):
    'Install brew.'

    clazz._check_macos()

  @classmethod
  def ensure(clazz):
    'Ensure brew is installed.'

    clazz._check_macos()
    
  @classmethod
  def _check_macos(clazz):
    if host.SYSTEM == host.MACOS:
      return
    raise brew_error('brew is only for macos')

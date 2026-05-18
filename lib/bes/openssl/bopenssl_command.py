#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.system_command import system_command

from .bopenssl_error import bopenssl_error

class bopenssl_command(system_command):

  @classmethod
  def exe_name(clazz):
    return 'openssl'

  @classmethod
  def extra_path(clazz):
    return None

  @classmethod
  def error_class(clazz):
    return bopenssl_error

  @classmethod
  def static_args(clazz):
    return None

  @classmethod
  def supported_systems(clazz):
    return ( 'linux', 'macos' )

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.check import check
from bes.system.log import logger

from . import uv_installer_options as uv_installer_options_module

class uv_installer_base(object, metaclass=ABCMeta):

  _log = logger('uv_installer')

  def __init__(self, options):
    check.check_uv_installer_options(options)
    self.options = options

  @abstractmethod
  def install(self, version=None):
    'Install uv. version=None means latest.'
    raise NotImplementedError('install')

  @abstractmethod
  def uninstall(self):
    'Remove uv from the system.'
    raise NotImplementedError('uninstall')

  @abstractmethod
  def is_installed(self):
    'Return True if uv is installed.'
    raise NotImplementedError('is_installed')

  @abstractmethod
  def installed_version(self):
    'Return the installed uv version string, or None if not installed.'
    raise NotImplementedError('installed_version')

  @abstractmethod
  def exe_path(self):
    'Return the absolute path to the uv binary, or None if not installed.'
    raise NotImplementedError('exe_path')

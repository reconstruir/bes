#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.execute import execute

from .platform_determiner_base import platform_determiner_base
from .linux_os_release import linux_os_release
from .linux_lsb_release import linux_lsb_release

class platform_determiner_linux(platform_determiner_base):

  def __init__(self, platform):
    impl = self._make_impl(platform)
    if not impl:
      raise RuntimeError('Unknown linux system: %s - %s' % (str(platform)))
    self._impl = impl

  @classmethod
  def _make_impl(self, platform):
    if linux_os_release.has_os_release():
      filename, content = linux_os_release.read_os_release()
      from .platform_determiner_linux_os_release import platform_determiner_linux_os_release
      return platform_determiner_linux_os_release(platform, content, filename)
    elif linux_lsb_release.has_lsb_release():
      lsb_release = linux_lsb_release.lsb_release_output()
      return platform_determiner_linux_lsb_release(platform, lsb_release)
    else:
      return None
    
  @classmethod
  def _lsb_release_exe(clazz):
    try:
      return execute.execute('which lsb_release').stdout.strip()
    except Exception as ex:
      return None
    
  @classmethod
  def _lsb_release_output(clazz):
    return execute.execute('lsb_release -v -a').stdout
    
  @classmethod
  def _etc_issue_content(clazz):
    try:
      with open('/etc/issue', 'r') as fin:
        return fin.read()
    except Exception as ex:
      return None
    
  #@abstractmethod
  def system(self):
    'system.'
    return self._impl.system()

  #@abstractmethod
  def distro(self):
    'distro.'
    return self._impl.distro()
  
  #@abstractmethod
  def family(self):
    'distro family.'
    return self._impl.family()

  #@abstractmethod
  def distributor(self):
    'the distro distributor.'
    return self._impl.distributor()
  
  #@abstractmethod
  def codename(self):
    'distro codename.'
    return self._impl.codename()

  #@abstractmethod
  def version(self):
    'distro version.'
    return self._impl.version()

  #@abstractmethod
  def arch(self):
    'arch.'
    return self._impl.arch()

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class linux_arch(object):
  'Linux arch'

  @classmethod
  def arch(clazz, platform):
    'Return the linux platform arch.'
    arch = platform.machine()
    if arch.startswith('armv7'):
      return 'armv7'
    return arch
  

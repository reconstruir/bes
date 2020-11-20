#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check

from .softwareupdater import softwareupdater

class softwareupdater_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(softwareupdater_cli_command, command)
    return func(**kargs)
  
  @classmethod
  def available(clazz):
    items = softwareupdater.available()
    for item in items:
      print('{} - {} - {}'.format(item.label, item.version, item.size))
    return 0

  @classmethod
  def install(clazz, label):
    check.check_string(label)

    softwareupdater.install(label)
    return 0
  

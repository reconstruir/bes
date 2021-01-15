#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

class process_info(namedtuple('process_info', 'user, pid, cpu, mem, vsz, rss, tty, command')):

  def __new__(clazz, user, pid, cpu, mem, vsz, rss, tty, command):
    return clazz.__bases__[0].__new__(clazz, user, pid, cpu, mem, vsz, rss, tty, command)

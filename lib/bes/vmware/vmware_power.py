#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .vmware_error import vmware_error

class vmware_power(object):

  STATES = ( 'start', 'stop', 'reset', 'suspend', 'pause', 'unpause' )

  @classmethod
  def is_valid(clazz, state):
    check.check_string(state)

    return state in clazz.STATES

  @classmethod
  def check_state(clazz, state):
    check.check_string(state)

    if not clazz.is_valid(state):
      raise vmware_error('Invalid power state "{}" - Should be one of: {}'.format(state, ' '.join(clazz.STATES)))
    return state

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

class criteria(object):
  'criteria for finding files.'

  __metaclass__ = ABCMeta

  FILTER = 1
  STOP = 2

  VALID_ACTIONS = [ FILTER, STOP ]
  
  FILE = 0x1
  DIR = 0x2
  ANY = FILE | DIR

  VALID_TARGETS = [ FILE, DIR, ANY ]
  
  def __init__(self, action = FILTER, target = ANY):
    self.action = self.check_action(action)
    self.target = self.check_target(target)
  
  @abstractmethod
  def matches(self, variables):
    pass

  def targets_files(self):
    return (self.target & self.FILE) != 0
  
  def targets_dirs(self):
    return (self.target & self.DIR) != 0
  
  @classmethod
  def action_is_valid(clazz, action):
    return action in clazz.VALID_ACTIONS

  @classmethod
  def check_action(clazz, action):
    if not clazz.action_is_valid(action):
      raise ValueError('invalid action: %s' % (str(action)))
    return action

  @classmethod
  def target_is_valid(clazz, target):
    return target in clazz.VALID_TARGETS

  @classmethod
  def check_target(clazz, target):
    if not clazz.target_is_valid(target):
      raise ValueError('invalid target: %s' % (str(target)))
    return target
  

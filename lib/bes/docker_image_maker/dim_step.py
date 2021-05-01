#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#
class dim_step(object):
  'Class to share code between scripts that build and test automation images.'

  STEP_NAMES = (
    'base',
    'builder',
    'egoist_builder',
    'egoist',
    'bes_tester',
  )

  STEPS_BUILD_ORDER = {
    'builder': 0,
    'base': 1,
    'egoist_builder': 2,
    'egoist': 3,
    'bes_tester': 4,
  }

  @classmethod
  def step_name_is_valid(clazz, step_name):
    return step_name in clazz.STEP_NAMES

  @classmethod
  def check_step_name(clazz, step_name):
    if not clazz.step_name_is_valid(step_name):
      raise ValueError('Invalid step_name: "{}" - should be one of {}'.format(step_name, ' '.join(clazz.STEP_NAMES)))
    return step_name
  
  @classmethod
  def resolve_steps(clazz, steps):
    return sorted(steps or clazz.STEP_NAMES, key = lambda i: clazz.STEPS_BUILD_ORDER[i])

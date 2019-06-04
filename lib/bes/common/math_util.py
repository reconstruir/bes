#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class math_util(object):
  'Math util'

  @classmethod
  def clamp(clazz, value, min_value, max_value):
    'Clamp value to be within min and max.'
    if value < min_value:
      value = min_value
    elif value > max_value:
      value = max_value
    return value

  @classmethod
  def value_to_percent(clazz, value, min_value, max_value):
    'Return value as percent.'
    if not type(min_value) == type(max_value):
      raise TypeError('min_value and max_value should be of the same type instead of: %s %s' % (type(min_value), type(max_value)))
    value = float(value)
    min_value = float(min_value)
    max_value = float(max_value)
    value_range = max_value - min_value
    percent = ((value - min_value) / value_range) * 100.0
    return clazz.clamp(percent, 0.0, 100.0)

  @classmethod
  def percent_to_value(clazz, percent, min_value, max_value):
    'Return value from percent.'
    if not type(min_value) == type(max_value):
      raise TypeError('min_value and max_value should be of the same type instead of: %s %s' % (type(min_value), type(max_value)))
    percent = float(percent)
    min_value = float(min_value)
    max_value = float(max_value)
    value_range = max_value - min_value
    value = (percent / 100.0 * value_range) + min_value
    if isinstance(min_value, int):
      value = int(value + 0.5)
    return clazz.clamp(value, min_value, max_value)

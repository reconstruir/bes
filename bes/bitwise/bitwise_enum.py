#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bitwise_unpack import bitwise_unpack

class _bitwise_enum_meta(type):

  def __new__(meta, name, bases, class_dict):
    print "__new__: ", name
    clazz = type.__new__(meta, name, bases, class_dict)
#    if not hasattr(clazz, 'SIZE'):
#      raise TypeError('Enum subclass does not define SIZE: %s' % (clazz.__name__))
#    if not hasattr(clazz, 'VALUES'):
#      raise TypeError('Enum subclass does not define VALUES: %s' % (clazz.__name__))
    size = getattr(clazz, 'SIZE', 1)
    if size not in [ 1, 2, 4, 8 ]:
      raise TypeError('Invalid SIZE.  Should be 1, 2, 4 or 8: %s' % (size))

    print "DIR: ", dir(clazz)
    print "DICT: ", clazz.__dict__
    #
    #values = getattr(clazz, 'VALUES')
#    if not isinstance(values, ( tuple ) size not in [ 1, 2, 4, 8 ]:
#      raise TypeError('Invalid SIZE.  Should be 1, 2, 4 or 8: %s' % (size))
    #message_registry.register_class(clazz)
    return clazz

class bitwise_enum(object):

  __metaclass__ = _bitwise_enum_meta

  def __init__(self, value = None):
    self._value = value

  def write_to_io(self, io):
    pass
    
  def read_from_io(self):
    pass
    #self._assert size in [ 1, 2, 4, 8]
    #return bitwise_unpack.unpack(self._stream.read(size), size, endian = self._endian)

#!/usr/bin/env python
#-*- coding:utf-8 -*-

#TODO: implement for class method http://blog.dscpl.com.au/2014/01/the-missing-synchronized-decorator.html

from functools import wraps

# http://code.activestate.com/recipes/577105-synchronization-decorator-for-class-methods/
def synchronized_method(lock_name):
  'A decarator that locks the given lock while the decorated class method is running and'
  'unlocks when it is done.  It handles the case where the function raises an exception'
  'The lock is specified by name and expected to be an attribute of the instance'
  def _wrap(func):
    @wraps(func)
    def _caller(self, *args, **kwargs):
      lock = self.__getattribute__(lock_name)
      assert lock, 'Instance "%s" needs to have a "%s" attribute' % (self, lock_name)
      lock.acquire()
      try:
        return func(self, *args, **kwargs)
      finally:
        lock.release()
    return _caller
  return _wrap

# http://code.activestate.com/recipes/465057-basic-synchronization-decorator/
def synchronized_function(lock):
  'A decarator that locks the given lock while the decorated function is running and'
  'unlocks when it is done.  It handles the case where the function raises an exception'
  def _wrap(f):
    def _caller(*args, **kw):
      lock.acquire()
      try:
        return f(*args, **kw)
      finally:
        lock.release()
    return _caller
  return _wrap

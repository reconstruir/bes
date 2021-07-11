

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

def _dec(f):
  def wrapper(*args):
    return f(*args)
  return wrapper

class cookie(object):
  def __init__(self, something):
    self.something = something

  @_dec
  def get(self, n):
    print('get: {}'.format(n))
    return 56

c = cookie('666')
c.get(9)
raise SystemExit(0)
        
class _dec(object):
  def __init__(self, function):
    self._function = function

  def __call__(self, *args, **kwargs):
    #help(self._function)
    return self._function(*args)
    return 0

class cookie(object):

  def __init__(self):
    pass

  @_dec
  def foo(self, f1):
    print('foo')
    return None

  def bar(self):
    print('bar')
    return None
  

a = cookie()
a.foo(666)
a.bar()

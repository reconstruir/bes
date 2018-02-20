
import os

class thing(object):

  def __init__(self, c):
    #v = os.environ.get('CACA', None)
    #print('v: %s' % (v))
    code = 'from .color import color'
    print('code: %s' % (code))
    xlocals = {}
    exec(code, globals(), xlocals)
    print('xlocals: %s' % (xlocals))
    #    from .color import color as vaca
#    clazz = xglobals['vaca']
#    print('clazz: %s' % (clazz))
    self.color = c #color.BLUE

  def __str__(self):
    return self.color

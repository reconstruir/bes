#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class code(object):
  'Class to deal with python code.'

  @classmethod
  def execfile(clazz, filename, exec_globals, exec_locals):
    try:      
      with open(filename, 'r') as f:
        content = f.read()
    except Exception as ex:
      raise
    clazz.exectext(filename, content, exec_globals, exec_locals)

  @classmethod
  def exectext(clazz, filename, text, exec_globals, exec_locals):
    c = compile(text, filename, 'exec')
    exec(c, exec_globals, exec_locals)

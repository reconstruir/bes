#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, tempfile
from os_env import os_env

class env_override(object):

  def __init__(self, env = None):
    self._original_env = os_env.clone_current_env()
    self._stack = []
    if env:
      self.update(env)
    
  def __enter__(self):
    return self
  
  def __exit__(self, type, value, traceback):
    self.reset()
    
  def reset(self):
    os_env.set_current_env(self._original_env)

  def push(self):
    self._stack.append(os_env.clone_current_env())

  def pop(self):
    d = self._stack.pop()
    os_env.set_current_env(d)

  def set(self, key, value):
    os.environ[key] = value
    
  def get(self, key, default_value = None):
    return os.environ.get(key, default_value)
    
  def update(self, d):
    os.environ.update(d)

  @classmethod
  def temp_home(clazz):
    'Return an env_override object with a temporary HOME'
    tmp_dir = tempfile.mkdtemp(suffix = '.home')
    return env_override(env = { 'HOME': tempfile.mkdtemp(suffix = '.home') })

#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class blurb_mixin:
  '''
  Mixin to add easy blurb and blurb with log methods to a class
  Assumes "_blurber" and "_log" instance or class objects exist
  '''
  
  def blurb(self, *args, **kargs):
    self._blurber.blurb(*args, **kargs)

  def blurb_verbose(self, *args, **kargs):
    self._blurber.blurb_verbose(*args, **kargs)

  def blurb_log_c(self, *args, **kargs):
    self._blurber.blurb_verbose(*args, **kargs)
    self._log.log_c(*args, **kargs)
    
  def blurb_log_d(self, *args, **kargs):
    self._blurber.blurb_verbose(*args, **kargs)
    self._log.log_d(*args, **kargs)
    
  def blurb_log_e(self, *args, **kargs):
    self._blurber.blurb_verbose(*args, **kargs)
    self._log.log_e(*args, **kargs)

  def blurb_log_i(self, *args, **kargs):
    self._blurber.blurb_verbose(*args, **kargs)
    self._log.log_i(*args, **kargs)

  def blurb_log_w(self, *args, **kargs):
    self._blurber.blurb_verbose(*args, **kargs)
    self._log.log_w(*args, **kargs)

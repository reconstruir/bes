#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from .blurb import blurb

class blurber(object):

  def __init__(self, label):
    self._label = label

  def set_verbose(self, verbose):
    blurb.set_verbose(verbose)

  def set_label_length(self, label_length):
    blurb.set_label_length(label_length)

  def blurb(self, message, output = None, fit = False):
    blurb.blurb(self._label, message, output = output, fit = fit)
    
  def blurb_verbose(self, message, output = None, fit = False):
    blurb.blurb_verbose(self._label, message, output = output, fit = fit)
    
  def set_process_name(self, process_name):
    blurb.set_process_name(label_length)

check.register_class(blurber, include_seq = False)    

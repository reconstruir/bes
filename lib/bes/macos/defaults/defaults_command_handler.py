#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.system.check import check

from .defaults import defaults

class defaults_command_handler(bcli_command_handler):

  def name(self):
    return 'defaults'

  def _command_get_domain(self, domain, style, options):
    check.check_string(domain)
    check.check_string(style)

    s = defaults.get_domain(domain, style)
    print(s)
    return 0

  def _command_get_value(self, domain, key, options):
    check.check_string(domain)
    check.check_string(key)

    s = defaults.get_value(domain, key)
    print(s)
    return 0

  def _command_set_value(self, domain, key, value, options):
    check.check_string(domain)
    check.check_string(key)
    check.check_string(value)

    defaults.set_value(domain, key, value)
    return 0

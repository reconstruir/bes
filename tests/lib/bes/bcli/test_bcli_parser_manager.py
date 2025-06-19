#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.testing.unit_test import unit_test

from bes.bcli.bcli_parser_manager import bcli_parser_manager
from bes.bcli.bcli_parser_maker_i import bcli_parser_maker_i

class test_bcli_parser_manager(unit_test):

  class _kiwi_parser_maker(bcli_parser_maker_i):
    @classmethod
    #@abstractmethod
    def make_parser(clazz):
      p = argparse.ArgumentParser()
      p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                     help = 'Verbose output [ False ]')
      p.add_argument('-d', '--debug', action = 'store_true', default = False,
                     help = 'Debug mode [ False ]')
      p.add_argument('--mean', action = 'store', type = float, default = 0.0,
                     help = 'Minimum mean for each frame to process [ 0.0 ]')
    
  def test_register_parser(self):
    m = bcli_parser_manager()
    m.register_parser([ 'fruit', 'kiwi' ], self._kiwi_parser_maker)

    p = m.find_parser([ 'fruit', 'kiwi' ])
    print(p)
    
if __name__ == '__main__':
  unit_test.main()

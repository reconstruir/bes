#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.common.command_line_cli import command_line_cli

class test_command_line_cli(unittest.TestCase):

  def test_simple(self):
    class food(command_line_cli):

      FOO = 666

      def __init__(self):
        super(food, self).__init__('foods')

      def command_foo(self, what):
        print("command_foo(%s)" % (what))
        return 0
      
      def command_bar(self, what):
        print("command_bar(%s)" % (what))
        return 0
      
    f = food()
    self.assertEqual( 0, f.run() )
        
if __name__ == "__main__":
  unittest.main()

#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.common import command_line


class test_command_line(unittest.TestCase):

  def test_simple(self):
    class food(command_line):

      FOO = 666

      def __init__(self):
        super(food, self).__init__('foods')

      def command_foo(self, what):
        print "command_foo(%s)" % (what)
        return 0
      
      def command_bar(self, what):
        print "command_bar(%s)" % (what)
        return 0
      
    f = food()
    self.assertEqual( 0, f.run() )
        
if __name__ == "__main__":
  unittest.main()

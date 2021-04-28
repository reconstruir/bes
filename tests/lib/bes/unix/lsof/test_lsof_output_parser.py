#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.unix.lsof.lsof_output_parser import lsof_output_parser as P

class test_lsof_output_parser(unit_test):

  def test_parse_lsof_output(self):
    text = '''\
COMMAND     PID   USER   FD      TYPE             DEVICE  SIZE/OFF                NODE NAME
loginwind   168 fred  cwd       DIR                1,5       736                   2 /
loginwind   168 fred  txt       REG                1,5    240512            12483574 /private/var/db/Assets.car
loginwind   168 fred  txt       REG                1,5   1566832 1152921500312434482 /usr/lib/dyld
loginwind   168 fred    2u      CHR                3,2  0t252826                 310 /dev/null
loginwind   168 fred    3r      REG                1,5    331944 1152921500312072668 /System/com.example.foo
UserEvent   327 fred    3u     unix 0x1593087a21ff2ebf       0t0                     ->0x1593087a2f690247
UserEvent   327 fred    4   NPOLICY                                                  
UserEvent   327 fred    5u     unix 0x1593087a2f6903d7       0t0                     ->0x1593087a2f6900b7
UserEvent   327 fred    6u   KQUEUE                                                  count=0, state=0x8
rapportd    346 fred    7u     IPv4 0x1593087a7741e19f       0t0                 TCP *:49648 (LISTEN)
'''
    self.assertEqual( [
      ( 'loginwind', 168, 'fred', 'cwd', 'DIR', None ),
      ( 'loginwind', 168, 'fred', 'txt', 'REG', 'rivate/var/db/Assets.car' ),
      ( 'loginwind', 168, 'fred', 'txt', 'REG', 'sr/lib/dyld' ),
      ( 'loginwind', 168, 'fred', '2u', 'CHR', 'ev/null' ),
      ( 'loginwind', 168, 'fred', '3r', 'REG', 'ystem/com.example.foo' ),
      ( 'UserEvent', 327, 'fred', '3u', 'unix', '0x1593087a2f690247' ),
      ( 'UserEvent', 327, 'fred', '4', 'NPOLICY', None ),
      ( 'UserEvent', 327, 'fred', '5u', 'unix', '0x1593087a2f6900b7' ),
      ( 'UserEvent', 327, 'fred', '6u', 'KQUEUE', 'unt=0, state=0x8' ),
      ( 'rapportd', 346, 'fred', '7u', 'IPv4', '49648 (LISTEN)' ),
    ], P.parse_lsof_output(text) )
    
if __name__ == '__main__':
  unit_test.main()

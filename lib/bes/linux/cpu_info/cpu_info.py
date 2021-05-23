# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#import os.path as path

from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
#from bes.property.cached_property import cached_property
from bes.common.type_checked_list import type_checked_list
#from bes.common.json_util import json_util

from bes.text.text_line_parser import text_line_parser

#processor	: 0
#vendor_id	: GenuineIntel
#cpu family	: 6
#model		: 158
#model name	: Intel(R) Core(TM) i9-9880H CPU @ 2.30GHz
#stepping	: 13
#microcode	: 0xde
#cpu MHz		: 2304.000
#cache size	: 16384 KB
#physical id	: 0
#siblings	: 1
#core id		: 0
#cpu cores	: 1
#apicid		: 0
#initial apicid	: 0
#fpu		: yes
#fpu_exception	: yes
#cpuid level	: 22
#wp		: yes
#flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon nopl xtopology tsc_reliable nonstop_tsc cpuid pni pclmulqdq vmx ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand hypervisor lahf_lm abm 3dnowprefetch cpuid_fault invpcid_single ssbd ibrs ibpb stibp ibrs_enhanced tpr_shadow vnmi ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 invpcid rdseed adx smap clflushopt xsaveopt xsavec xgetbv1 xsaves arat md_clear flush_l1d arch_capabilities
#vmx flags	: vnmi invvpid ept_x_only ept_ad tsc_offset vtpr mtf ept vpid unrestricted_guest ple ept_mode_based_exec
#bugs		: spectre_v1 spectre_v2 spec_store_bypass swapgs itlb_multihit srbds
#bogomips	: 4608.00
#clflush size	: 64
#cache_alignment	: 64
#address sizes	: 45 bits physical, 48 bits virtual
#power management:

class cpu_info(object):
  'Class to store cpu info about one cpu on linux'

  class _cpu_info_values(object):
    pass
  
  def __init__(self, values):
    check.check_dict(values)

    self._values = self._cpu_info_values()
    for key, value in values.items():
      setattr(self._values, key, value)

  @property
  def values(self):
    return self._values
    
  @property
  def flags(self):
    return self._values.flags

  @property
  def processor(self):
    return self._values.processor
  
  @classmethod
  def parse_text(clazz, text):
    check.check_string(text)

    lines = text_line_parser.parse_lines(text, strip_text = True, remove_empties = True)
    values = {}
    for line in lines:
      key, delimiter, value = line.partition(':')
      key = key.strip()
      value = value.strip()
      values[key] = clazz._parse_value(key, value)
    return cpu_info(values)

  @classmethod
  def _parse_value(clazz, key, value):
    if key == 'flags':
      value = set(string_util.split_by_white_space(value, strip = True))
    else:
      try:
        value = int(value)
      except ValueError as ex:
        pass
    return value
  
check.register_class(cpu_info, include_seq = False)

class cpu_info_list(type_checked_list):

  __value_type__ = cpu_info
  
  def __init__(self, values = None):
    super(cpu_info_list, self).__init__(values = values)

  @classmethod
  def parse_text(clazz, text):
    check.check_string(text)

    values = cpu_info_list()
    chunks = text.strip().split('\n\n')
    for chunk in chunks:
      value = cpu_info.parse_text(chunk)
      values.append(value)
    return values
  
check.register_class(cpu_info_list, include_seq = False)

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.unit_test import unit_test
from bes.config.simple_config import simple_config as SC
from bes.config.simple_config_loader import simple_config_loader as SCL
from bes.fs.testing.temp_content import temp_content
from bes.system.env_override import env_override

class test_simple_config_loader(unit_test):

  def test_section(self):
    tmp_dir = self._make_temp_configs()
    s = SCL(tmp_dir, '*.config')
    s.load()
    files = [
      'animal.config',
      'bacteria.config',
      'bird.config',
      'cat.config',
      'dog.config',
      'mammal.config',
      'organism.config',
      'virus.config',
    ]
    self.assertEqual( files, [ f.filename for f in s.files ] )
    s = s.section('cat')
    self.assertEqual( 'true', s.find_by_key('food') )
    self.assertEqual( 'true', s.find_by_key('pet') )
    self.assertEqual( 'warm', s.find_by_key('blood') )
    self.assertEqual( 'aerobic', s.find_by_key('respiration') )
    
  def _make_temp_configs(self):
    organism = '''\
organism
  respiration: unknown
  food: false
'''
    animal = '''\
animal extends organism
  respiration: aerobic
  food: false
'''
    bacteria = '''\
bacteria extends organism
  respiration: anaerobic
'''
    virus = '''\
virus extends organism
  respiration: parasitic
'''
    bird = '''\
bird extends animal
  blood: cold
  food: true
'''
    mammal = '''\
mammal extends animal
  blood: warm
  food: maybe
'''
    dog = '''\
dog extends mammal
  food: false
  pet: true
'''
    cat = '''\
cat extends mammal
  food: true
  pet: true
'''
    tmp_dir = temp_content.write_items_to_temp_dir([
      'file organism.config "{}" 644'.format(organism),
      'file animal.config "{}" 644'.format(animal),
      'file bacteria.config "{}" 644'.format(bacteria),
      'file virus.config "{}" 644'.format(virus),
      'file bird.config "{}" 644'.format(bird),
      'file mammal.config "{}" 644'.format(mammal),
      'file dog.config "{}" 644'.format(dog),
      'file cat.config "{}" 644'.format(cat),
    ])
    return tmp_dir
      
if __name__ == '__main__':
  unit_test.main()

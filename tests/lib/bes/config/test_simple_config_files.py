#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.unit_test import unit_test
from bes.config.simple_config import simple_config as SC
from bes.config.simple_config_files import simple_config_files as SCL
from bes.config.simple_config_error import simple_config_error as ERROR
from bes.fs.testing.temp_content import temp_content
from bes.fs.file_util import file_util
from bes.system.env_override import env_override

class test_simple_config_files(unit_test):

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
    self.assertEqual( 'false', s.section('dog').find_by_key('food') )
    self.assertEqual( 'true', s.section('dog').find_by_key('pet') )
    self.assertEqual( 'warm', s.section('dog').find_by_key('blood') )
    self.assertEqual( 'aerobic', s.section('dog').find_by_key('respiration') )
    
    self.assertEqual( 'true', s.section('cat').find_by_key('food') )
    self.assertEqual( 'true', s.section('cat').find_by_key('pet') )
    self.assertEqual( 'warm', s.section('cat').find_by_key('blood') )
    self.assertEqual( 'aerobic', s.section('cat').find_by_key('respiration') )

    self.assertEqual( 'true', s.section('bird').find_by_key('food') )
    self.assertEqual( 'false', s.section('bird').find_by_key('pet') )
    self.assertEqual( 'cold', s.section('bird').find_by_key('blood') )
    self.assertEqual( 'aerobic', s.section('bird').find_by_key('respiration') )

  def test_section_one_config_file(self):
    tmp_file = self._make_one_temp_config()
    s = SCL(path.dirname(tmp_file), '*.config')
    s.load()
    self.assertEqual( 'false', s.section('dog').find_by_key('food') )
    self.assertEqual( 'true', s.section('dog').find_by_key('pet') )
    self.assertEqual( 'warm', s.section('dog').find_by_key('blood') )
    self.assertEqual( 'aerobic', s.section('dog').find_by_key('respiration') )
    
    self.assertEqual( 'true', s.section('cat').find_by_key('food') )
    self.assertEqual( 'true', s.section('cat').find_by_key('pet') )
    self.assertEqual( 'warm', s.section('cat').find_by_key('blood') )
    self.assertEqual( 'aerobic', s.section('cat').find_by_key('respiration') )

    self.assertEqual( 'true', s.section('bird').find_by_key('food') )
    self.assertEqual( 'false', s.section('bird').find_by_key('pet') )
    self.assertEqual( 'cold', s.section('bird').find_by_key('blood') )
    self.assertEqual( 'aerobic', s.section('bird').find_by_key('respiration') )

  def test_files(self):
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
    self.assertEqual( [ path.join(tmp_dir, f) for f in files ], s.files )
    
  def test_files_one_config_file(self):
    tmp_file = self._make_one_temp_config()
    s = SCL(path.dirname(tmp_file), '*.config')
    s.load()
    self.assertEqual( [ tmp_file ], s.files )
    
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
  pet: false
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

  def _make_one_temp_config(self):
    content = '''\
organism
  respiration: unknown
  food: false

animal extends organism
  respiration: aerobic
  food: false
  pet: false

bacteria extends organism
  respiration: anaerobic

virus extends organism
  respiration: parasitic

bird extends animal
  blood: cold
  food: true

mammal extends animal
  blood: warm
  food: maybe

dog extends mammal
  food: false
  pet: true

cat extends mammal
  food: true
  pet: true
'''
    tmp_dir = self.make_temp_dir()
    tmp_file = path.join(tmp_dir, 'organisms.config')
    file_util.save(tmp_file, content = content)
    return tmp_file

  def test_duplicate_section(self):
    content = '''\
organism
  respiration: unknown
  food: false

organism
  respiration: unknown
  food: true
'''
    tmp_dir = self.make_temp_dir()
    tmp_file = path.join(tmp_dir, 'organisms.config')
    file_util.save(tmp_file, content = content)
    s = SCL(tmp_dir, '*.config')
    with self.assertRaises(ERROR) as ctx:
      s.load()
      self.assertTrue( 'Duplicate config section' in ctx.exception.message )

  def test_missing_dependency(self):
    content = '''\
ape extends missing_link
  something: yes
'''
    tmp_dir = self.make_temp_dir()
    tmp_file = path.join(tmp_dir, 'organisms.config')
    file_util.save(tmp_file, content = content)
    s = SCL(tmp_dir, '*.config')
    s.load()
    with self.assertRaises(ERROR) as ctx:
      s.section('ape')
      self.assertTrue( 'Missing dependency for ape: missing_link' in ctx.exception.message )
      
  def test_cyclic_dependency(self):
    content = '''\
ape extends bonobo
  something: yes

bonobo extends ape
  something: yes
'''
    tmp_dir = self.make_temp_dir()
    tmp_file = path.join(tmp_dir, 'organisms.config')
    file_util.save(tmp_file, content = content)
    s = SCL(tmp_dir, '*.config')
    s.load()
    with self.assertRaises(ERROR) as ctx:
      s.section('ape')
      self.assertTrue( 'Cyclic dependencies found: ape bonobo' in ctx.exception.message )
      
if __name__ == '__main__':
  unit_test.main()

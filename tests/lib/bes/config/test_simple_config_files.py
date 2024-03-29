#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.config.simple_config import simple_config as SC
from bes.config.simple_config_error import simple_config_error as ERROR
from bes.config.simple_config_files import simple_config_files as SCL
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.testing.temp_content import temp_content
from bes.system.env_override import env_override
from bes.testing.unit_test import unit_test
from bes.system.host import host
from bes.testing.unit_test_function_skip import unit_test_function_skip

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
    self.assertTrue( s.has_unique_section('dog') )
    self.assertTrue( s.has_unique_section('cat') )
    self.assertFalse( s.has_unique_section('notthere') )
    
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

shepherd extends dog
  food: false
  pet: false
  worker: true
  name: rin tin tin
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
    tmp_file = path.join(tmp_dir, 'apes.config')
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
    tmp_file = path.join(tmp_dir, 'apes.config')
    file_util.save(tmp_file, content = content)
    s = SCL(tmp_dir, '*.config')
    s.load()
    with self.assertRaises(ERROR) as ctx:
      s.section('ape')
      self.assertTrue( 'Cyclic dependencies found: ape bonobo' in ctx.exception.message )
      
  def test_self_dependency(self):
    content = '''\
ape extends ape
  something: yes
'''
    tmp_dir = self.make_temp_dir()
    tmp_file = path.join(tmp_dir, 'apes.config')
    file_util.save(tmp_file, content = content)
    s = SCL(tmp_dir, '*.config')
    with self.assertRaises(ERROR) as ctx:
      s.load()
      self.assertTrue( 'Self dependency for "ape"' in ctx.exception.message )

  def test_env_vars(self):
    content = '''\
ape
  activity: ${_CONFIG_ACTIVITY}
  snack: leaves

bonobo extends ape
  activity: loving
  snack: ${_CONFIG_SNACK}

chimp extends ape
  activity: fighting
  snack: eggs
'''
    tmp_dir = self.make_temp_dir()
    tmp_file = path.join(tmp_dir, 'apes.config')
    file_util.save(tmp_file, content = content)
    with env_override(env = { '_CONFIG_ACTIVITY': 'resting', '_CONFIG_SNACK': 'kiwi' }) as tmp_env:
      s = SCL(tmp_dir, '*.config')
      s.load()
      self.assertEqual( 'fighting', s.section('chimp').find_by_key('activity') )
      self.assertEqual( 'loving', s.section('bonobo').find_by_key('activity') )
      self.assertEqual( 'eggs', s.section('chimp').find_by_key('snack') )
      self.assertEqual( 'kiwi', s.section('bonobo').find_by_key('snack') )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_search_path_expanduser(self):
    content = '''\
ape
  activity: resting
  snack: leaves

bonobo extends ape
  activity: loving
  snack: kiwi

chimp extends ape
  activity: fighting
  snack: eggs
'''
    with env_override.temp_home() as tmp_env:
      file_util.save(path.join(os.environ['HOME'], '.config', 'apes.config'), content = content)
      s = SCL('~/.config', '*.config')
      s.load()
      self.assertEqual( 'fighting', s.section('chimp').find_by_key('activity') )
      self.assertEqual( 'loving', s.section('bonobo').find_by_key('activity') )
      self.assertEqual( 'eggs', s.section('chimp').find_by_key('snack') )
      self.assertEqual( 'kiwi', s.section('bonobo').find_by_key('snack') )
      
  def test_search_path_env_var(self):
    content = '''\
ape
  activity: resting
  snack: leaves

bonobo extends ape
  activity: loving
  snack: kiwi

chimp extends ape
  activity: fighting
  snack: eggs
'''
    tmp_file = self.make_named_temp_file('apes.config', content = content)
    with env_override(env = { '_CONFIG_DIR': path.dirname(tmp_file) }) as tmp_env:
      s = SCL('${_CONFIG_DIR}', '*.config')
      s.load()
      self.assertEqual( 'fighting', s.section('chimp').find_by_key('activity') )
      self.assertEqual( 'loving', s.section('bonobo').find_by_key('activity') )
      self.assertEqual( 'eggs', s.section('chimp').find_by_key('snack') )
      self.assertEqual( 'kiwi', s.section('bonobo').find_by_key('snack') )
      
  def test_empty_section(self):
    content = '''\
ape
  activity: resting
  snack: leaves

bonobo extends ape

chimp extends ape
  activity: fighting
  snack: eggs
'''
    tmp_file = self.make_named_temp_file('apes.config', content = content)
    with env_override(env = { '_CONFIG_DIR': path.dirname(tmp_file) }) as tmp_env:
      s = SCL('${_CONFIG_DIR}', '*.config')
      s.load()
      self.assertEqual( 'fighting', s.section('chimp').find_by_key('activity') )
      self.assertEqual( 'resting', s.section('bonobo').find_by_key('activity') )
      self.assertEqual( 'eggs', s.section('chimp').find_by_key('snack') )
      self.assertEqual( 'leaves', s.section('bonobo').find_by_key('snack') )

  def test_load_and_find_section(self):
    tmp_dir = self._make_temp_configs()
    section = SCL.load_and_find_section(tmp_dir, 'mammal', 'config')
    self.assertEqual( {
      'food': 'maybe',
      'blood': 'warm',
      'pet': 'false',
      'respiration': 'aerobic',
    }, section.to_dict() )

  def test_load_config_without_section(self):
    tmp_dir = self._make_temp_configs()
    tmp_config = path.join(tmp_dir, 'mammal.config')
    values = SCL.load_config(tmp_config)
    self.assertEqual( {
      'food': 'maybe',
      'blood': 'warm',
      'pet': 'false',
      'respiration': 'aerobic',
    }, values )

  def test_load_config_with_section(self):
    tmp_dir = self._make_temp_configs()
    tmp_config = path.join(tmp_dir, 'mammal.config') + ':shepherd'
    values = SCL.load_config(tmp_config)
    self.assertEqual( {
      'food': 'false',
      'blood': 'warm',
      'pet': 'false',
      'worker': 'true',
      'respiration': 'aerobic',
      'name': 'rin tin tin',
    }, values )

  def test_load_config_with_none(self):
    self.assertEqual( {}, SCL.load_config(None) )
    
if __name__ == '__main__':
  unit_test.main()

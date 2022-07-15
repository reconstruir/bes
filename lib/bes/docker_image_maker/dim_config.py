#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#

from os import path

from ..system.check import check

class dim_config(object):

  def __init__(self, script, config_dir, system):
    self._script = script
      
    self.all_systems_config = self._load_config(script, config_dir, 'systems.config')

    if not self.all_systems_config.has_unique_section(system):
      script.error('Missing system config for "{}": {}'.format(system, 'config/systems.config'))

    self.config = self.all_systems_config.section(system)

    self.python_module_versions = self._load_config(script, config_dir, 'python_module_versions.config')
    self.steps = self._load_config(script, config_dir, 'steps.config')
    self.artifacts = self._load_config(script, config_dir, 'artifacts.config')
    self.versions = self._load_config(script, config_dir, 'versions.config')

  @classmethod
  def _load_config(self, script, config_dir, basename):
    filename = path.join(config_dir, basename)
    if not path.isfile(filename):
      script.error('Config file not found: {}'.format(filename))
    return script.simple_config.from_file(filename)

  @property
  def system_name(self):
    return self.config.system_name

  @property
  def system_version(self):
    return self.config.system_version

  @property
  def image_version(self):
    return self.config.image_version

  def step_version(self, step_name):
    return self.steps.section(step_name).version

  @property
  def step_env(self):
    env = {}
    for section_name in self.steps.section_names():
      key = 'EGO_STEP_{}_VERSION'.format(section_name.upper())
      env[key] = self.steps.section(section_name).version
    return env 

  @property
  def dockerfile_env(self):
    env = {}
    for section_name in self.steps.section_names():
      key = 'EGO_DOCKERFILE_STEP_{}_VERSION'.format(section_name.upper())
      env[key] = self.steps.section(section_name).version
    return env 
  

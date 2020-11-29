#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# We need to explicitly import each module otherwise PyInstaller will not
# include them in the egoist binary.
from .cst_install_brew import cst_install_brew

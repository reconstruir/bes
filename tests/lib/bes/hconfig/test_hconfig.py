#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.testing.unit_test import unit_test
from bes.hconfig.hconfig import hconfig
from bes.hconfig.hconfig_error import hconfig_error
from bes.hconfig.hconfig_type_int import hconfig_type_int
from bes.hconfig.hconfig_type_float import hconfig_type_float
from bes.hconfig.hconfig_type_base import hconfig_type_base
from bes.system.check import check

class test_hconfig(unit_test):

  def test_basic(self):
    d = {
      'timestamp': '666',
      'fruit': {
        'kiwi': { 'color': 'green', 'flavor': 'tart' },
        'apple': { 'color': 'red', 'flavor': 'sweet' },
        'lemon': { 'color': 'yellow', 'flavor': 'tart' },
      },
      'wine': {
        'barolo': { 'color': 'red', 'body': 'medium' },
        'bordeaux': { 'color': 'red', 'body': 'full' },
        'sancerre': { 'color': 'white', 'body': 'light' },
      },
    }
    c = hconfig(d)
    self.assertEqual( '666', c.timestamp )
    self.assertEqual( 'green', c.fruit.kiwi.color )
    with self.assertRaises(hconfig_error) as ctx:
      c.fruit.kiwi.price

  def test_register_type(self):
    d = {
      'timestamp': '666',
      'fruit': {
        'kiwi': { 'color': 'green', 'flavor': 'tart', 'price': '1.2' },
        'apple': { 'color': 'red', 'flavor': 'sweet', 'price': '0.9' },
        'lemon': { 'color': 'yellow', 'flavor': 'tart', 'price': '0.5' },
      },
      'wine': {
        'barolo': { 'color': 'red', 'body': 'medium', 'price': '42' },
        'bordeaux': { 'color': 'red', 'body': 'full', 'price': '777' },
        'sancerre': { 'color': 'white', 'body': 'light', 'price': '33' },
      },
    }
    c = hconfig(d)
    c.register_type('timestamp', hconfig_type_int)
    c.register_type('*.*.price', hconfig_type_float)

    self.assertEqual( 666, c.timestamp )
    self.assertEqual( 1.2, c.fruit.kiwi.price )
    self.assertEqual( 777, c.wine.bordeaux.price )

  def test_register_type_cast_dict(self):
    d = {
      'timestamp': '666',
      'fruit': {
        'kiwi': { 'color': 'green', 'flavor': 'tart', 'price': '1.2' },
        'apple': { 'color': 'red', 'flavor': 'sweet', 'price': '0.9' },
        'lemon': { 'color': 'yellow', 'flavor': 'tart', 'price': '0.5' },
      },
      'wine': {
        'barolo': { 'color': 'red', 'body': 'medium', 'price': '42' },
        'bordeaux': { 'color': 'red', 'body': 'full', 'price': '777' },
        'sancerre': { 'color': 'white', 'body': 'light', 'price': '33' },
      },
    }
    _fruit = namedtuple('_fruit', 'color, flavor, price')
    class _fruit_type(hconfig_type_base):
      @classmethod
      #@abstractmethod
      def cast(clazz, value, root):
        return _fruit(value.color, value.flavor, value.price)

    c = hconfig(d)
    c.register_type('timestamp', hconfig_type_int)
    c.register_type('fruit.*', _fruit_type)
    c.register_type('fruit.*.price', hconfig_type_float)

    self.assertEqual( _fruit('green', 'tart', 1.2), c.fruit.kiwi )

  def test_register_type_cast_dict_deep(self):
    d = {
      'country': {
        'italy': {
          'piedmont': {
            'barbera': {
              'color': 'red',
              'body': 'medium',
              'price': '36',
            },
            'grignolino': {
              'color': 'red',
              'body': 'light',
              'price': '27.50',
            },
            'nebbiolo': {
              'color': 'red',
              'body': 'medium',
              'price': '42.42',
              'points': 99,
              'notes': [
                { 'tag': 'tasting', 'blurb': 'yummy' },
                { 'tag': 'budget', 'blurb': 'expensive' },
              ],
            },
          },
          'tuscany': {
            'brunello': {
              'color': 'red',
              'body': 'medium',
              'price': '88.40',
            },
            'chianti': {
              'color': 'red',
              'body': 'light',
              'price': '30.33',
            },
          },
        },
        'france': {
          'burgundy': {
            'chablis': {
              'color': 'white',
              'body': 'light',
              'price': '45.60',
            },
            'Côte de Nuits': {
              'color': 'red',
              'body': 'medium',
              'price': '99.99',
            },
          },
          'rhone': {
            'chateauneuf du pape': {
              'color': 'red',
              'body': 'medium',
              'price': '66.34',
            },
            'gigondas': {
              'color': 'red',
              'body': 'medium',
              'price': '34.45',
            },
          },
        }
      }
    }
    _wine = namedtuple('_wine', 'color, body, price, points')
    class _wine_type(hconfig_type_base):
      @classmethod
      #@abstractmethod
      def cast(clazz, value, root):
        try:
          points = value.points
        except hconfig_error as ex:
          points = None
        return _wine(value.color, value.body, value.price, value.points)
    _wine_note = namedtuple('_wine_note', 'tag, blurb, points')
    class _wine_note_type(hconfig_type_base):
      @classmethod
      #@abstractmethod
      def cast(clazz, value, root):
        return _wine_note(value.tag, value.blurb, value.points)

    c = hconfig(d)
    c.register_type('country.*.*.*', _wine_type)
    c.register_type('country.*.*.*.price', hconfig_type_float)
    c.register_type('country.*.*.*.notes.*', _wine_note_type)
    c.register_type('country.*.*.*.points', hconfig_type_int)
    
    self.assertEqual( _wine('red', 'medium', 42.42, 99),
                      c.country.italy.piedmont.nebbiolo )
    self.assertEqual( 42.42, c.country.italy.piedmont.nebbiolo.price )
    
if __name__ == '__main__':
  unit_test.main()

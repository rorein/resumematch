from unittest import TestCase
from copy import deepcopy

from ...matching import match, Matcher, cmatch, CompilingMatcher

class TestMatch(TestCase):

   class TestData:
      def __init__(self, pattern=None, objs=None, exps=None):
         self.pattern = pattern
         self.objs = objs
         self.exps = exps

      def test(self, tc, func):
         for obj, exp in zip(self.objs, self.exps):
            score = func(self.pattern, obj)
            tc.assertEqual(score,exp)

      def copy(self):
         return deepcopy(self)

   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.dict_tests = []
      self.list_tests = []
      self.tests = []

      dict_test_1 = TestMatch.TestData()
      dict_test_1.pattern = {
         'a':1,
         'b':2,
         'c':3
      }
      dict_test_1.objs = [
         {
            'a':1
         },
         {
            'a':1,
            'b':3
         },
         {
            'a':1,
            'b':2
         },
         {
            'a':1,
            'b':2,
            'z':87
         }
      ]
      dict_test_1.exps = [1/3, 1/3, 2/3, 2/3]
      self.dict_tests.append(dict_test_1)

      dict_test_2 = dict_test_1.copy()
      dict_test_2.pattern['_id'] = 1337
      dict_test_2.objs.append({'_id':1337})
      dict_test_2.exps.append(0)
      self.dict_tests.append(dict_test_2)

      list_test_1 = TestMatch.TestData()
      list_test_1.pattern = ['a', 'b', 'c', 'd']
      list_test_1.objs = [
         ['a',],
         ['a', 'b', 'e'],
         ['d', 'c', 'a', 'b'],
         ['e', 'f', 'g']
      ]
      list_test_1.exps = [1/4, 1/2, 1, 0]
      self.list_tests.append(list_test_1)
      
      list_test_2 = TestMatch.TestData()
      list_test_2.pattern = ['a', 'a', 'b']
      list_test_2.objs = [
         ['a'],
         ['b'],
         ['a', 'b'],
         ['a', 'b', 'b'],
         ['a', 'a'],
         ['a', 'a', 'b']
      ]
      list_test_2.exps = [2/3, 1/3, 1, 1, 2/3, 1]
      self.list_tests.append(list_test_2)


   def test_match(self):
      for dt in self.dict_tests:
         dt.test(self, match)
      for lt in self.list_tests:
         lt.test(self, match)
      for t in self.tests:
         t.test(self, match)

   def test_type_handling(self):
      @match.add_handler
      def match_int(pat: int, obj: int):
         if pat != 0:
            return obj / pat
         return obj

      self.dict_tests[0].exps = [1/3, 2.5/3, 2/3, 2/3]
      self.dict_tests[1].exps = [1/3, 2.5/3, 2/3, 2/3, 0]

      self.test_match()

   def test_cmatch(self):
      for dt in self.dict_tests:
         dt.test(self, cmatch)
      for lt in self.list_tests:
         lt.test(self, cmatch)
      for t in self.tests:
         t.test(self, cmatch)

   def test_type_chandling(self):
      @cmatch.add_chandler
      def match_int(cpat: int, obj: int):
         if cpat != 0:
            return obj / cpat
         return obj

      self.dict_tests[0].exps = [1/3, 2.5/3, 2/3, 2/3]
      self.dict_tests[1].exps = [1/3, 2.5/3, 2/3, 2/3, 0]

      self.test_cmatch()



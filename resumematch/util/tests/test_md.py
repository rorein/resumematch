from unittest import TestCase
from typing import Union

from ...util import *

class TestMultiDispatch(TestCase):

   def test_md(self):
      testfunc = MultiLDispatcher(2)

      @testfunc.add
      def fun1(a: int, b: int):
         return a + b

      @testfunc.add
      def fun2(a: str, b: int):
         return a * b

      @testfunc.add
      def fun3(a, b):
         return a

      @testfunc.add
      def fun4(a: str, b: str):
         return a in b

      @testfunc.add
      def fun5(a: int, b: float):
         return a - b

      @testfunc.add
      def fun6(a: int, b):
         return b


      @testfunc.add
      def fun7(a: float, b: Union[int, float]):
         return a / b
   
      tests = [
      (testfunc(1, 2), 3),
      (testfunc('a', 2), 'aa'),
      (testfunc({}, 2345), {}),
      (testfunc('2', 'a'), False),
      (testfunc(1, 2.0), -1.0),
      (testfunc(1.0, 2.0), 0.5),
      (testfunc(1, {}), {}),
      (testfunc([], (1,)), []),
      (testfunc(1.0, 3), 1/3)
      ]

      for test in tests:
         self.assertEqual(*test)




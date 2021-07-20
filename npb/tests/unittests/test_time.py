import os
import spiceypy
import unittest
from unittest import TestCase
from npb.utils.time import dsk_coverage

class TestTime(TestCase):

    @classmethod
    def setUpClass(cls):
        '''
        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        '''
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

    def setUp(self):
        '''
        This method will be executed before each test function.
        '''
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")
        
        lsk_file = '../data/kernels/lsk/naif0012.tls'
        spiceypy.furnsh(lsk_file)

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)
        
        spiceypy.kclear()

    def test_dsk_coverage(self):
        
        dsk_file = '../data/kernels/dsk/DEIMOS_K005_THO_V01.BDS'

        [start_time_cal, stop_time_cal] = \
            dsk_coverage(dsk_file)
        
        self.assertEqual((start_time_cal, 
                          stop_time_cal), 
                         ('1950-01-01T00:00:00.001Z', 
                          '2049-12-31T23:59:58.999Z'))

if __name__ == '__main__':

    unittest.main()
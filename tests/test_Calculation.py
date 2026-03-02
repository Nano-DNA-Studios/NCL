import unittest
import os
from ncl import Calculation, InputFile

class CalculationTests(unittest.TestCase):
    
    def setUp(self):
        
        self.name = "Propane"
        self.extension = ".inp"
        self.inputFileName = "Propane.inp"
        self.outputFileName = "Propane.out"
        
        self.inputFile = InputFile(self.name, self.extension)
        self.baseCachePath = os.path.join(os.getcwd(), "Cache")
        
    def test_constructor(self):
        
        calculation = Calculation(self.inputFile)
        
        self.assertIsNotNone(calculation)
        self.assertEqual(self.inputFile, calculation.inputFile)
        self.assertEqual(self.baseCachePath, calculation.baseCachePath)
        
    def test_constructor_error(self):
        
        with self.assertRaises(TypeError):
            Calculation("")
            
    def test_getInputFileName(self):
        
        calculation = Calculation(self.inputFile)
        
        self.assertEqual(self.inputFileName, calculation.getInputFileName())
        
    def test_getOutputFileName(self):
        
        calculation = Calculation(self.inputFile)
        
        self.assertEqual(self.outputFileName, calculation.getOutputFileName())
        
    def test_calculate_error(self):
        
        calculation = Calculation(self.inputFile)
        
        with self.assertRaises(NotImplementedError):
            calculation.calculate()
    
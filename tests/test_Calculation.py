import unittest
import os
from ncl import Calculation, InputFile, Molecule

# I use a dummy class because InputFile is abstract
class DummyInputFile(InputFile):
    def build(self) -> str:
        return "dummy content"

class CalculationTests(unittest.TestCase):
    
    def setUp(self):
        self.name = "Propane"
        self.extension = ".inp"
        self.inputFileName = "Propane.inp"
        self.outputFileName = "Propane.out"
        
        self.molecule = Molecule(self.name, "tests/Resources/Propane.xyz")
        self.inputFile = DummyInputFile(self.name, self.extension, self.molecule)
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
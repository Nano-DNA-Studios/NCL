import unittest
import os
from ncl import OrcaCalculation, OrcaInputFile, Molecule

class OrcaCalculationTest(unittest.TestCase):
    
    def setUp(self):
        
        self.name = "Propane"
        self.filePath = "tests/Resources/Propane.xyz"
        
        self.molecule = Molecule(self.name, self.filePath)
        self.inputFile = OrcaInputFile(self.name, self.molecule)
        
        self.baseCachePath = os.path.join(os.getcwd(), "Cache")
        self.cachePath = os.path.join(self.baseCachePath, "Orca", self.name)
        
        return super().setUp()
    
    def test_constructor(self):
        
        calculation = OrcaCalculation(self.inputFile)
        
        self.assertIsNotNone(calculation)
        self.assertEqual(self.inputFile, calculation.inputFile)
        self.assertEqual(self.baseCachePath, calculation.baseCachePath)
        self.assertEqual(self.cachePath, calculation.cachePath)
        
    def test_constructor_error(self):
        
        with self.assertRaises(TypeError):
            OrcaCalculation("")
    
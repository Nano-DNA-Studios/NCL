import unittest
import os
from ncl import Molecule, OrcaInputFile, OrcaDockerCalculation

class OrcaDockerCalculationTest(unittest.TestCase):
    
    def setUp(self):
        
        self.name = "Propane"
        self.filePath = "tests/Resources/Propane.xyz"
        self.containerName = "ncrlorca"
        self.imageName = "mrdnalex/orca"
        
        self.molecule = Molecule(self.name, self.filePath)
        self.inputFile = OrcaInputFile(self.name, self.molecule)
        
        self.baseCachePath = os.path.join(os.getcwd(), "Cache")
        self.cachePath = os.path.join(self.baseCachePath, "Orca", self.name)
    
    def test_constructor(self):
        
        calculation = OrcaDockerCalculation(self.inputFile)
        
        self.assertIsNotNone(calculation)
        self.assertEqual(self.inputFile, calculation.inputFile)
        self.assertEqual(self.baseCachePath, calculation.baseCachePath)
        self.assertEqual(self.cachePath, calculation.cachePath)
        
        self.assertEqual(self.containerName, calculation.containerName)
        self.assertEqual(self.imageName, calculation.imageName)
     
    def test_constructor_error(self):
        
        with self.assertRaises(TypeError):
            OrcaDockerCalculation("")

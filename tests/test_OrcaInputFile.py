import unittest
from ncl import OrcaInputFile, Molecule

class OrcaInputFileTest(unittest.TestCase):
    
    def setUp(self):
        
        self.name = "Propane"
        self.filePath = "tests/Resources/Propane.xyz"
        self.molecule = Molecule(self.name , self.filePath)
        
        self.HF_Keyword = "HF"
        self.basis= "DEF2-SVP"
        self.functional = "B3LYP"
        self.HF_Header = "!HF DEF2-SVP B3LYP"
        
        self.inputFile = OrcaInputFile(self.name, self.molecule)
        
        pass
    
    def test_constructor(self):
        
        inputFile = OrcaInputFile(self.name, self.molecule)
        
        self.assertEqual(self.name, inputFile.name)
        self.assertEqual(self.molecule, inputFile.molecule)
        
        self.assertEqual("", inputFile._header)
        self.assertEqual("", inputFile._footer)
        self.assertEqual(1, len(inputFile._structures))
        
    def test_constructor_error(self):
        
        with self.assertRaises(TypeError):
            OrcaInputFile(1, self.molecule)
            
        with self.assertRaises(TypeError):
            OrcaInputFile(self.name, "")
            
        with self.assertRaises(ValueError):
            OrcaInputFile("", self.molecule)
        
        with self.assertRaises(ValueError):
            OrcaInputFile(" ", self.molecule)
            
    def test_setHartreeFock(self):
        
        inputFile = self.inputFile
        
        inputFile.setHartreeFock(self.basis, self.functional)
        
        self.assertEqual(self.HF_Header, inputFile._header)
        self.assertTrue(self.HF_Keyword in inputFile._header)
        self.assertTrue(self.basis in inputFile._header)
        self.assertTrue(self.functional in inputFile._header)
        
        self.assertEqual(1, len(inputFile._structures))
        
        self.assertEqual("", inputFile._footer)
        
    def test_setHartreeFock_error(self):
        
        inputFile = self.inputFile
        
        with self.assertRaises(TypeError):
            inputFile.setHartreeFock(1, self.functional)
            
        with self.assertRaises(TypeError):
            inputFile.setHartreeFock(self.basis, 1)
            
        with self.assertRaises(ValueError):
            inputFile.setHartreeFock("", self.functional)
            
        with self.assertRaises(ValueError):
            inputFile.setHartreeFock(self.basis, "")
            
        with self.assertRaises(ValueError):
            inputFile.setHartreeFock(" ", self.functional)
            
        with self.assertRaises(ValueError):
            inputFile.setHartreeFock(self.basis, " ")
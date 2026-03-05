import unittest
from ncl import OrcaInputFile, Molecule

class OrcaInputFileTest(unittest.TestCase):
    
    def setUp(self):
        self.name = "Propane"
        self.filePath = "tests/Resources/Propane.xyz"
        self.molecule = Molecule(self.name, self.filePath)
        self.molecule.charge = 0
        self.molecule.multiplicity = 1 
        
        self.inputFile = OrcaInputFile(self.name, self.molecule)
    
    def test_constructor(self):
        """Tests the initialization of the Orca lists and dicts"""
        self.assertEqual(self.name, self.inputFile.name)
        self.assertEqual(self.molecule, self.inputFile.molecule)
        self.assertListEqual([], self.inputFile.keywordCommands)
        self.assertDictEqual({}, self.inputFile.blocks)
        
    def test_constructor_error(self):
        with self.assertRaises(TypeError):
            OrcaInputFile(1, self.molecule)
            
        with self.assertRaises(TypeError):
            OrcaInputFile(self.name, "Not a Molecule")
            
        with self.assertRaises(ValueError):
            OrcaInputFile("", self.molecule)
            
    def test_addRoute(self):
        """Tests adding granular route commands"""
        self.inputFile.addRoute("Opt")
        self.assertIn("Opt", self.inputFile.keywordCommands)
        
    def test_addRoute_error(self):
        with self.assertRaises(ValueError):
            self.inputFile.addRoute("")
            
    def test_addBlock(self):
        """Tests adding granular blocks"""
        self.inputFile.addBlock("pal", "nprocs 8")
        self.assertEqual("nprocs 8", self.inputFile.blocks["pal"])
            
    def test_setHartreeFock(self):
        """Tests the Level 2 Helper Method"""
        basis = "DEF2-SVP"
        self.inputFile.setHartreeFock(basis)
        
        self.assertIn("HF", self.inputFile.keywordCommands)
        self.assertIn(basis, self.inputFile.keywordCommands)
        
    def test_setHartreeFock_error(self):
        with self.assertRaises(ValueError):
            self.inputFile.setHartreeFock("")
            
        with self.assertRaises(ValueError):
            self.inputFile.setHartreeFock(123)
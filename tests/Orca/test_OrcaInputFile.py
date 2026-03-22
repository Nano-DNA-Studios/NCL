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
            
    def test_setGeometryOptimization(self):
        """Tests the Level 2 Helper Method"""
        method = "B3LYP"
        basis = "DEF2-SVP"
        self.inputFile.setGeometryOptimization(method, basis)
        
        self.assertIn("OPT", self.inputFile.keywordCommands)
        self.assertIn(method, self.inputFile.keywordCommands)
        self.assertIn(basis, self.inputFile.keywordCommands)
        
    def test_setGeometryOptimization_error(self):
        with self.assertRaises(ValueError):
            self.inputFile.setGeometryOptimization("", "DEF2-SVP")
            
        with self.assertRaises(ValueError):
            self.inputFile.setGeometryOptimization("B3LYP", "")
            
    def test_setFrequencyCalculation(self):
        """Tests the Level 2 Helper Method"""
        method = "B3LYP"
        basis = "DEF2-SVP"
        self.inputFile.setFrequencyCalculation(method, basis)
        
        self.assertIn("FREQ", self.inputFile.keywordCommands)
        self.assertIn(method, self.inputFile.keywordCommands)
        self.assertIn(basis, self.inputFile.keywordCommands)
        
    def test_setFrequencyCalculation_error(self):
        with self.assertRaises(ValueError):
            self.inputFile.setFrequencyCalculation("", "DEF2-SVP")
            
        with self.assertRaises(ValueError):
            self.inputFile.setFrequencyCalculation("B3LYP", "")
            
    def test_setSinglePointEnergy(self):
        """Tests the Level 2 Helper Method"""
        method = "B3LYP"
        basis = "DEF2-SVP"
        self.inputFile.setSinglePointEnergy(method, basis)
        
        self.assertIn(method, self.inputFile.keywordCommands)
        self.assertIn(basis, self.inputFile.keywordCommands)
        
    def test_setSinglePointEnergy_error(self):
        with self.assertRaises(ValueError):
            self.inputFile.setSinglePointEnergy("", "DEF2-SVP")
            
        with self.assertRaises(ValueError):
            self.inputFile.setSinglePointEnergy("B3LYP", "")
            
    def test_addBlock_error(self):
        """Tests that addBlock throws TypeErrors for invalid non-string inputs"""
        with self.assertRaises(TypeError):
            self.inputFile.addBlock(123, "content")
            
        with self.assertRaises(TypeError):
            self.inputFile.addBlock("pal", 123)

    def test_setMethod(self):
        """Tests the base setMethod clearing, uppercasing, and *extras appending logic"""
        # Add a dummy command to ensure it gets cleared
        self.inputFile.addRoute("OldCommand")
        
        self.inputFile.setMethod("b3lyp", "def2-svp", "TightSCF", "Grid5")
        
        self.assertNotIn("OldCommand", self.inputFile.keywordCommands)
        self.assertIn("B3LYP", self.inputFile.keywordCommands) # Checks forced uppercase
        self.assertIn("def2-svp", self.inputFile.keywordCommands)
        self.assertIn("TightSCF", self.inputFile.keywordCommands)
        self.assertIn("Grid5", self.inputFile.keywordCommands)

    def test_setParallelProcessing(self):
        """Tests the parallel processing block generator logic"""
        # Should ignore requests for 1 or fewer cores
        self.inputFile.setParallelProcessing(1)
        self.assertNotIn("pal", self.inputFile.blocks)
        
        # Should build the block for > 1 cores
        self.inputFile.setParallelProcessing(8)
        self.assertIn("pal", self.inputFile.blocks)
        self.assertEqual("nprocs 8", self.inputFile.blocks["pal"])

    def test_build(self):
        """Tests the final string generation of the Orca input file"""
        # Setup a dummy calculation state
        self.inputFile.setSinglePointEnergy("B3LYP", "DEF2-SVP")
        self.inputFile.setParallelProcessing(4)
        
        outputString = self.inputFile.build()
        lines = outputString.split("\n")
        
        # 1. Verify the Keyword Command Line
        self.assertTrue(lines[0].startswith("! B3LYP DEF2-SVP"))
        
        # 2. Verify the Block Section
        self.assertIn("%pal", lines)
        self.assertIn("nprocs 4", lines)
        
        # Since order in dicts can vary slightly, we just verify "end" exists
        self.assertIn("end", lines)
        
        # 3. Verify the Coordinate Section
        self.assertIn(f"* xyz {self.molecule.charge} {self.molecule.multiplicity}", lines)
        
        # Verify the actual atom content made it into the string
        self.assertIn(self.molecule.getContent(), outputString)
        
        # Verify it terminates properly
        self.assertTrue(outputString.strip().endswith("*"))
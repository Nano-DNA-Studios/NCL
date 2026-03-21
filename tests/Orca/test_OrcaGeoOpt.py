import io
import os
import unittest
from ncl import Molecule
from unittest.mock import patch, MagicMock
from ncl.Orca.Pipelines import OrcaGeoOpt, OrcaGeoOptCalculationResults

class OrcaGeoOptCalculationResultsTest(unittest.TestCase):
    
    def setUp(self):
        self.molecule = Molecule("Propane", "tests/Resources/Propane.xyz")

    def test_constructor(self):
        """Tests the initialization and attribute assignment of the Results object"""
        results = OrcaGeoOptCalculationResults(15.5, "Success")
        
        # Assign the custom attributes
        results.initial = self.molecule
        results.final = self.molecule
        results.iterations = [self.molecule]
        
        # Verify inherited and custom properties
        self.assertEqual(15.5, results.elapsed)
        self.assertEqual("Success", results.status)
        self.assertEqual(self.molecule, results.initial)
        self.assertEqual(self.molecule, results.final)
        self.assertEqual(1, len(results.iterations))


class OrcaGeoOptTest(unittest.TestCase):
    
    def setUp(self):
        # We instantiate a fresh molecule for each test
        self.molecule = Molecule("Propane", "tests/Resources/Propane.xyz")
        self.baseCachePath = os.path.join(os.getcwd(), "Cache")

    def test_constructor(self):
        """Tests the initialization of the Geometry Optimization Calculation"""
        calc = OrcaGeoOpt(self.molecule, "B3LYP", "DEF2-SVP", "TightSCF")
        
        self.assertEqual("Propane-GeoOpt", calc.initialMolecule.name)
        self.assertEqual("B3LYP", calc.method)
        self.assertEqual("DEF2-SVP", calc.basis)
        self.assertIn("TightSCF", calc.extras)
        self.assertTrue(calc.useDocker)
        self.assertEqual(1, len(calc.iterations))
        self.assertEqual(calc.initialMolecule, calc.iterations[0])
        self.assertIsNotNone(calc.inputFile)

    @patch('os.mkdir')
    @patch('os.path.exists')
    def test_setup(self, mockExists, mockMkdir):
        """Tests that setup correctly creates the nested cache path"""
        mockExists.return_value = False
        
        calc = OrcaGeoOpt(self.molecule, "B3LYP", "DEF2-SVP")
        calc.setup()
        
        mockMkdir.assert_called_with(calc.cachePath)

    def test_isOptimized(self):
        """Tests the optimization check logic based on vibrational frequencies"""
        calc = OrcaGeoOpt(self.molecule, "B3LYP", "DEF2-SVP")
        
        # All positive frequencies = Optimized
        self.assertTrue(calc.isOptimized([100.5, 200.0, 350.2]))
        
        # Contains a negative frequency = Not Optimized
        self.assertFalse(calc.isOptimized([100.5, -50.0, 350.2]))

    def test_getGeoOptInputFile(self):
        """Tests the generation of the iterative input files"""
        calc = OrcaGeoOpt(self.molecule, "B3LYP", "DEF2-SVP", "TightSCF")
        
        inputFile = calc.getGeoOptInputFile(self.molecule, 1)
        
        self.assertEqual("Propane-GeoOpt-1", inputFile.name)
        self.assertIn("OPT", inputFile.keywordCommands)
        self.assertIn("FREQ", inputFile.keywordCommands)
        self.assertIn("B3LYP", inputFile.keywordCommands)
        self.assertIn("DEF2-SVP", inputFile.keywordCommands)
        self.assertIn("TightSCF", inputFile.keywordCommands)

    def test_calculate_success(self):
        """Tests the calculation loop when it successfully optimizes on the first try"""
        
        # We use 'with patch' so we only mock dependencies inside this test block
        with patch('os.path.exists', return_value=True), \
             patch('os.mkdir'), \
             patch('ncl.Orca.Pipelines.OrcaGeoOpt.OrcaDockerCalculation') as mockDocker, \
             patch('ncl.Orca.Pipelines.OrcaGeoOpt.Molecule') as mockMolecule, \
             patch('ncl.Orca.Pipelines.OrcaGeoOpt.OrcaOutputFile') as mockOutputFile, \
             patch('sys.stdout', new_callable=io.StringIO):

            calc = OrcaGeoOpt(self.molecule, "B3LYP", "DEF2-SVP")

            # 1. Setup Mock Docker Calculation Result
            mockCalcInstance = mockDocker.return_value
            mockResult = MagicMock()
            mockResult.status = "Success"
            mockResult.outputFilePath = "/dummy/out.out"
            mockCalcInstance.calculate.return_value = mockResult
            mockCalcInstance.cachePath = "/dummy/cache"
            mockCalcInstance.inputFile.name = "Propane-GeoOpt-1"

            # 2. Setup Mock Molecule returned from the .xyz file
            mockMolInstance = MagicMock()
            mockMolecule.return_value = mockMolInstance

            # 3. Setup Mock Output File (All positive frequencies forces loop to break)
            mockOutInstance = mockOutputFile.return_value
            mockOutInstance.IRFrequencies = {"frequency": [100.0, 200.0]}

            # Run the calculation
            results = calc.calculate()

            self.assertEqual("Success", results.status)
            self.assertTrue(results.elapsed >= 0)
            self.assertEqual(calc.initialMolecule, results.initial)
            self.assertEqual(mockMolInstance, results.final)
            
            # Initial molecule + 1 successful loop iteration = 2
            self.assertEqual(2, len(results.iterations))

    def test_calculate_failure(self):
        """Tests that the calculation loop breaks gracefully if the Orca calculation fails"""
        
        with patch('os.path.exists', return_value=True), \
             patch('os.mkdir'), \
             patch('ncl.Orca.Pipelines.OrcaGeoOpt.OrcaDockerCalculation') as mockDocker, \
             patch('ncl.Orca.Pipelines.OrcaGeoOpt.Molecule') as mockMolecule, \
             patch('ncl.Orca.Pipelines.OrcaGeoOpt.OrcaOutputFile') as mockOutputFile, \
             patch('sys.stdout', new_callable=io.StringIO):

            calc = OrcaGeoOpt(self.molecule, "B3LYP", "DEF2-SVP")

            mockCalcInstance = mockDocker.return_value
            mockResult = MagicMock()
            
            # Status failure triggers the loop to break
            mockResult.status = "Failure" 
            mockResult.outputFilePath = "/dummy/out.out"
            mockCalcInstance.calculate.return_value = mockResult
            mockCalcInstance.cachePath = "/dummy/cache"
            mockCalcInstance.inputFile.name = "Propane-GeoOpt-1"

            # Negative frequency would normally continue the loop, but Failure overrides
            mockOutInstance = mockOutputFile.return_value
            mockOutInstance.IRFrequencies = {"frequency": [-50.0]} 

            results = calc.calculate()

            self.assertEqual("Failure", results.status)
            self.assertEqual(2, len(results.iterations))
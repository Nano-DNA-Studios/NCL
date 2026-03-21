import io
import os
import unittest
import subprocess
from unittest.mock import patch, call
from ncl import Molecule, OrcaInputFile, OrcaDockerCalculation
from ncl.Orca import OrcaCalculation

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

    @patch('subprocess.run')
    def test_remove(self, mockRun):
        """Tests that _remove sends the correct docker kill and rm commands"""
        calculation = OrcaDockerCalculation(self.inputFile)
        calculation._remove()
        
        # Verify subprocess.run was called twice with the expected commands
        calls = [
            call(
                f"docker kill {self.containerName}", 
                shell=True, 
                stderr=subprocess.DEVNULL, 
                stdout=subprocess.DEVNULL
            ),
            call(
                f"docker rm {self.containerName}", 
                shell=True, 
                stderr=subprocess.DEVNULL, 
                stdout=subprocess.DEVNULL
            )
        ]
        mockRun.assert_has_calls(calls, any_order=False)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('subprocess.run')
    @patch.object(OrcaDockerCalculation, '_remove')
    @patch.object(OrcaCalculation, 'setup')
    def test_calculate_success(self, mockSetup, mockRemove, mockRun, mockStdout):
        """Tests a successful execution of the Docker calculate method"""
        calculation = OrcaDockerCalculation(self.inputFile)
        results = calculation.calculate()
        
        # Verify dependencies were called
        mockSetup.assert_called_once()
        self.assertEqual(2, mockRemove.call_count) # Should be called before and after the run
        mockRun.assert_called_once() # The actual docker run command
        
        # Verify the result object
        self.assertEqual("Success", results.status)
        self.assertTrue(results.elapsed >= 0)
        
        expectedOutputPath = os.path.join(self.cachePath, self.name + ".out")
        self.assertEqual(expectedOutputPath, results.outputFilePath)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('subprocess.run')
    @patch.object(OrcaDockerCalculation, '_remove')
    @patch.object(OrcaCalculation, 'setup')
    def test_calculate_error(self, mockSetup, mockRemove, mockRun, mockStdout):
        """Tests that calculate catches exceptions and returns a Failure result"""
        # Force the subprocess to fail
        mockRun.side_effect = Exception("Simulated Docker failure")
        
        calculation = OrcaDockerCalculation(self.inputFile)
        results = calculation.calculate()
        
        # Verify dependencies were called
        mockSetup.assert_called_once()
        self.assertEqual(2, mockRemove.call_count) # Should be called before run and inside except block
        mockRun.assert_called_once()
        
        # Verify the result object handled the failure
        self.assertEqual("Failure", results.status)
        self.assertTrue(results.elapsed >= 0)
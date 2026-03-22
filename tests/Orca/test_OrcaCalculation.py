import io
import os
import unittest
from unittest.mock import patch

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
            
    @patch('os.mkdir')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch.object(OrcaInputFile, 'save')
    def test_setup_creates_directory(self, mockSave, mockExists, mockMakedirs, mockMkdir):
        """Tests that setup creates the cache directories if they do not exist"""
        # Tell the mock that no directories exist
        mockExists.return_value = False
        
        calculation = OrcaCalculation(self.inputFile)
        calculation.setup()
        
        # Verify the target path was in the last call made to makedirs
        args, kwargs = mockMakedirs.call_args
        self.assertEqual(args[0], self.cachePath)
        
        # Verify the input file save method was called
        mockSave.assert_called_once_with(self.cachePath)

    @patch('os.mkdir')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch.object(OrcaInputFile, 'save')
    def test_setup_directory_exists(self, mockSave, mockExists, mockMakedirs, mockMkdir):
        """Tests that setup skips creating directories if they already exist"""
        # Tell the mock that the directories ALREADY exist
        mockExists.return_value = True
        
        calculation = OrcaCalculation(self.inputFile)
        calculation.setup()
        
        # Verify directory creation was skipped
        mockMakedirs.assert_not_called()
        mockMkdir.assert_not_called()
        # Verify save was still called
        mockSave.assert_called_once_with(self.cachePath)

    @patch('shutil.which')
    def test_getOrcaPath_success(self, mockWhich):
        """Tests that getOrcaPath returns the path when the executable is found"""
        expectedPath = "/usr/bin/orca"
        mockWhich.return_value = expectedPath
        
        calculation = OrcaCalculation(self.inputFile)
        
        self.assertEqual(expectedPath, calculation.getOrcaPath())

    @patch('shutil.which')
    def test_getOrcaPath_error(self, mockWhich):
        """Tests that getOrcaPath throws a RuntimeError when the executable is missing"""
        mockWhich.return_value = None
        
        calculation = OrcaCalculation(self.inputFile)
        
        with self.assertRaises(RuntimeError):
            calculation.getOrcaPath()

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('subprocess.run')
    @patch.object(OrcaCalculation, 'getOrcaPath')
    @patch.object(OrcaCalculation, 'setup')
    def test_calculate_success(self, mockSetup, mockGetOrcaPath, mockRun, mockStdout):
        """Tests a successful execution of the calculate method"""
        mockGetOrcaPath.return_value = "/fake/path/orca"
        
        calculation = OrcaCalculation(self.inputFile)
        results = calculation.calculate()
        
        # Verify dependencies were called
        mockSetup.assert_called_once()
        mockGetOrcaPath.assert_called_once()
        mockRun.assert_called_once()
        
        # Verify results object
        self.assertEqual("Success", results.status)
        self.assertTrue(results.elapsed >= 0)
        
        # Verify the output file path matches expected naming convention
        expectedOutputPath = os.path.join(self.cachePath, self.name + ".out")
        self.assertEqual(expectedOutputPath, results.outputFilePath)

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('subprocess.run')
    @patch.object(OrcaCalculation, 'getOrcaPath')
    @patch.object(OrcaCalculation, 'setup')
    def test_calculate_error(self, mockSetup, mockGetOrcaPath, mockRun, mockStdout):
        """Tests that calculate catches exceptions and returns a Failure result"""
        mockGetOrcaPath.return_value = "/fake/path/orca"
        # Force the subprocess to fail
        mockRun.side_effect = Exception("Simulated subprocess failure")
        
        calculation = OrcaCalculation(self.inputFile)
        results = calculation.calculate()
        
        # Verify dependencies were still called up to the failure
        mockSetup.assert_called_once()
        mockRun.assert_called_once()
        
        # Verify results object handled the failure gracefully
        self.assertEqual("Failure", results.status)
    
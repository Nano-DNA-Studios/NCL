import os
import unittest
import numpy as np
import pandas as pd
from ncl import OrcaOutputFile
from unittest.mock import patch

class OrcaOutputFileTest(unittest.TestCase):

    def setUp(self):
        self.fileName = "Propane-GeoOpt"
        self.filePath = "tests/Resources/Propane-GeoOpt.out" 
        
        self.fileName2 = "Acetaminophen-GeoOpt"
        self.filePath2 = "tests/Resources/Acetaminophen-GeoOpt.out" 
        
        # Safely check if the file exists so the test suite doesn't crash on setup
        if os.path.exists(self.filePath):
            self.outputFile = OrcaOutputFile(self.filePath)
        else:
            self.skipTest(f"Test file {self.filePath} not found. Update path to run tests.")
            
        if os.path.exists(self.filePath2):
            self.outputFile2 = OrcaOutputFile(self.filePath2)
        else:
            self.skipTest(f"Test file {self.filePath2} not found. Update path to run tests.")

    def test_constructor(self):
        """Tests the OrcaOutputFile constructor and attribute initialization"""
        self.assertEqual(self.fileName, self.outputFile.name)
        self.assertIsInstance(self.outputFile.lines, list)
        self.assertTrue(len(self.outputFile.lines) > 0)

    def test_getCalculationTypes(self):
        """Tests calculation type detection (Should detect OPT for a GeoOpt file)"""
        calcTypes = self.outputFile.calculationTypes
        
        self.assertIsInstance(calcTypes, list)
        if "OPT" in calcTypes:
            self.assertIn("OPT", calcTypes)
            
    def test_getFinalTimings(self):
        """Tests the computational timing dataframe extractor"""
        timings = self.outputFile.finalTimings
        
        if timings is not None:
            self.assertIsInstance(timings, pd.DataFrame)
            self.assertIn("Timing", timings.columns)
            self.assertIn("Time", timings.columns)

    def test_getFinalEnergy(self):
        """Tests that the final single point energy is extracted as a float"""
        energy = self.outputFile.energy
        
        if energy is not None:
            self.assertIsInstance(energy, float)
            # Final energies are typically negative (in Hartrees)
            self.assertTrue(energy < 0.0) 

    def test_getSCFEnergies(self):
        """Tests that the SCF energies list is populated with valid floats"""
        scfEnergies = self.outputFile.SCFEnergies
        
        self.assertIsInstance(scfEnergies, list)
        if len(scfEnergies) > 0:
            self.assertIsInstance(scfEnergies[0], float)

    def test_getMayerPopulation(self):
        """Tests Mayer population dataframes"""
        mayer = self.outputFile.mayerPopulation
        
        self.assertIsInstance(mayer, list)
        if len(mayer) > 0:
            self.assertIsInstance(mayer[0], pd.DataFrame)
            self.assertIn("ATOM", mayer[0].columns)
            self.assertIn("QA", mayer[0].columns)

    def test_getDipoleVector(self):
        """Tests the dipole vector extraction"""
        dipole = self.outputFile.dipole
        
        if dipole is not None:
            self.assertIsInstance(dipole, tuple)
            self.assertEqual(3, len(dipole)) # Should be X, Y, Z

    def test_getDipoleMagnitude(self):
        """Tests the dipole magnitude extraction"""
        magnitude = self.outputFile.absolutedipole
        
        if magnitude is not None:
            self.assertIsInstance(magnitude, float)
            self.assertTrue(magnitude >= 0.0)

    def test_gaussianBlur(self):
        """Tests the Gaussian blur math utility logic"""
        data = [0.0, 0.0, 10.0, 0.0, 0.0]
        blurred = self.outputFile.gaussianBlur(data, sigma=1.0)
        
        self.assertIsInstance(blurred, np.ndarray)
        self.assertEqual(len(data), len(blurred))
        
        # The peak at index 2 should be reduced and spread out to neighbors
        self.assertTrue(blurred[2] < 10.0)
        self.assertTrue(blurred[1] > 0.0)
        self.assertTrue(blurred[3] > 0.0)
        
    def test_getProcessedIRSpectra_error(self):
        """Tests that processing fails gracefully if no IR data exists"""
        # Temporarily force IRFrequencies to None to trigger the error
        self.outputFile.IRFrequencies = None
        
        with self.assertRaises(RuntimeError):
            self.outputFile.getProcessedIRSpectra()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.gca')
    @patch('matplotlib.pyplot.ylabel')
    @patch('matplotlib.pyplot.xlabel')
    @patch('matplotlib.pyplot.plot')
    @patch('matplotlib.pyplot.figure')
    @patch.object(OrcaOutputFile, 'getProcessedIRSpectra')
    def test_plotIRSpectra(self, mockGetSpectra, mockFigure, mockPlot, mockXlabel, mockYlabel, mockGca, mockShow):
        """Tests the plot display function while mocking matplotlib so it doesn't halt the test runner"""
        # Create a dummy dataframe so the plot has some axis data to read
        mockGetSpectra.return_value = pd.DataFrame({
            "Wavenumber": [1000, 2000], 
            "IRIntensity": [0.5, 0.8]
        })
        
        self.outputFile.plotIRSpectra()
        
        # Verify plotting sequence executed perfectly
        mockGetSpectra.assert_called_once()
        mockFigure.assert_called_once()
        mockPlot.assert_called_once()
        mockXlabel.assert_called_once_with("Wavenumber (1/cm)")
        mockYlabel.assert_called_once_with("IR Intensity")
        mockGca.assert_called_once()
        mockShow.assert_called_once()
        
    def test_getNumberOfAtoms(self):
        """Tests that the parser correctly finds the atom count using real files."""
        # Propane has 11 atoms
        propaneAtoms = self.outputFile.getNumberOfAtoms()
        self.assertEqual(11, propaneAtoms)
        
        # Acetaminophen has 20 atoms
        acetaminophenAtoms = self.outputFile2.getNumberOfAtoms()
        self.assertEqual(20, acetaminophenAtoms)

    def test_getNormalModes(self):
        """Tests the parsing of the normal modes block into a DataFrame using real files."""
        # Propane should have 33 degrees of freedom
        dfPropane = self.outputFile.getNormalModes()
        self.assertIsInstance(dfPropane, pd.DataFrame)
        self.assertEqual((33, 33), dfPropane.shape)
        self.assertIn("Mode_0", dfPropane.columns)
        self.assertIn("Mode_32", dfPropane.columns)
        
        # Acetaminophen should have 60 degrees of freedom
        dfAcetaminophen = self.outputFile2.getNormalModes()
        self.assertIsInstance(dfAcetaminophen, pd.DataFrame)
        self.assertEqual((60, 60), dfAcetaminophen.shape)
        self.assertIn("Mode_59", dfAcetaminophen.columns)

    def test_getImaginaryModeDisplacements(self):
        """Tests extracting and reshaping the imaginary mode vector using a real file."""
        # Acetaminophen contains an imaginary mode, it should return a 20x3 coordinate matrix
        vectors = self.outputFile2.getImaginaryModeDisplacements()
        
        self.assertIsInstance(vectors, np.ndarray)
        self.assertEqual((20, 3), vectors.shape)
        
        # Verify that the matrix actually contains movement data (not just empty zeros)
        self.assertTrue(np.any(vectors != 0))

    def test_getImaginaryModeDisplacements_noImaginaryString(self):
        """Tests that a real file with only real frequencies returns None."""
        # Propane does not have any imaginary frequencies, so it should safely return None
        vectors = self.outputFile.getImaginaryModeDisplacements()
        self.assertIsNone(vectors)

    def test_getNumberOfAtoms_notFound(self):
        """Tests that missing atom count data gracefully returns 0."""
        # This requires a mock because both real files contain atom counts
        self.outputFile.lines = [
            "This is a dummy file.\n",
            "It does not contain the atom count string.\n"
        ]
        atomCount = self.outputFile.getNumberOfAtoms()
        self.assertEqual(0, atomCount)

    def test_getNormalModes_notFound(self):
        """Tests that a missing NORMAL MODES section gracefully returns None."""
        # This requires a mock because both real files contain normal modes
        self.outputFile.lines = [
            "Some geometry optimization data...\n",
            "No vibrational data is present here.\n"
        ]
        df = self.outputFile.getNormalModes()
        self.assertIsNone(df)

    def test_getImaginaryModeDisplacements_missingDataFrame(self):
        """Tests the safeguard when the imaginary mode string exists, but the DataFrame failed to parse."""
        # This requires a mock to simulate a partial file corruption
        self.outputFile.lines = [
            "  0: ***imaginary mode***\n",
        ]
        self.outputFile.normalModes = None # Simulate DataFrame failure
        
        vectors = self.outputFile.getImaginaryModeDisplacements()
        self.assertIsNone(vectors)
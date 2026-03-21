import os
import unittest
import numpy as np
import pandas as pd
from ncl import OrcaOutputFile
from unittest.mock import patch

class OrcaOutputFileTest(unittest.TestCase):

    def setUp(self):
        self.fileName = "Propane-GeoOpt"
        # Update this path if the output file is located elsewhere in your project!
        self.filePath = "tests/Resources/Propane-GeoOpt.out" 
        
        # Safely check if the file exists so the test suite doesn't crash on setup
        if os.path.exists(self.filePath):
            self.outputFile = OrcaOutputFile(self.filePath)
        else:
            self.skipTest(f"Test file {self.filePath} not found. Update path to run tests.")

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
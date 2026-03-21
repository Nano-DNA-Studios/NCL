import unittest
from ncl import OrcaCalculationResults

class OrcaCalculationResultsTest(unittest.TestCase):
    
    def setUp(self):
        self.elapsedTimeSec = 15.5
        self.statusSuccess = "Success"
        self.statusFailed = "Failed"
        self.dummyFilePath = "/fake/path/to/Propane.out"

    def test_constructor(self):
        """Tests the initialization of the OrcaCalculationResults object"""
        results = OrcaCalculationResults(self.elapsedTimeSec, self.statusSuccess)
        
        self.assertAlmostEqual(self.elapsedTimeSec, results.elapsed)
        self.assertEqual(self.statusSuccess, results.status)

    def test_constructor_error(self):
        """Tests that the superclass error handling is properly triggered"""
        with self.assertRaises(TypeError):
            OrcaCalculationResults("not a float", self.statusSuccess)
            
        with self.assertRaises(TypeError):
            OrcaCalculationResults(self.elapsedTimeSec, 123)

    def test_outputFilePath_assignment(self):
        """Tests that the outputFilePath attribute can be assigned and accessed"""
        results = OrcaCalculationResults(self.elapsedTimeSec, self.statusSuccess)
        results.outputFilePath = self.dummyFilePath
        
        self.assertEqual(self.dummyFilePath, results.outputFilePath)
import unittest
from ncl import CalculationResults

class CalculationResultsTests(unittest.TestCase):
    
    def setUp(self):
        
        self.elapsedTimeSec = 10
        self.statusSuccess = "Success"
        self.statusFailed = "Failed"
        
    def test_constructor(self):
        
        calculationResultsSuccess = CalculationResults(self.elapsedTimeSec, self.statusSuccess)
        
        self.assertAlmostEqual(self.elapsedTimeSec, calculationResultsSuccess.elapsed)
        self.assertEqual(self.statusSuccess, calculationResultsSuccess.status)
        
        calculationResultsFailure = CalculationResults(self.elapsedTimeSec, self.statusFailed)
        
        self.assertAlmostEqual(self.elapsedTimeSec, calculationResultsFailure.elapsed)
        self.assertEqual(self.statusFailed, calculationResultsFailure.status)
        
    def test_constructor_error(self):
        
        with self.assertRaises(TypeError):
            CalculationResults("", self.statusSuccess)
            
        with self.assertRaises(TypeError):
            CalculationResults(self.elapsedTimeSec, 0)
            
        with self.assertRaises(TypeError):
            CalculationResults("", 0)
        
    def test_getCalculationTime(self):
            
        calculationResultsSec = CalculationResults(1, self.statusSuccess)
        self.assertEqual("1 second", calculationResultsSec.getCalculationTime())
        
        calculationResultsSec = CalculationResults(2, self.statusSuccess)
        self.assertEqual("2 seconds", calculationResultsSec.getCalculationTime())
        
        calculationResultsSec = CalculationResults(60, self.statusSuccess)
        self.assertEqual("1 minute", calculationResultsSec.getCalculationTime())
        
        calculationResultsSec = CalculationResults(120, self.statusSuccess)
        self.assertEqual("2 minutes", calculationResultsSec.getCalculationTime())
        
        calculationResultsSec = CalculationResults(3600, self.statusSuccess)
        self.assertEqual("1 hour", calculationResultsSec.getCalculationTime())
        
        calculationResultsSec = CalculationResults(7200, self.statusSuccess)
        self.assertEqual("2 hours", calculationResultsSec.getCalculationTime())
        
        calculationResultsSec = CalculationResults(86400, self.statusSuccess)
        self.assertEqual("1 day", calculationResultsSec.getCalculationTime())
        
        calculationResultsSec = CalculationResults(86400 * 2, self.statusSuccess)
        self.assertEqual("2 days", calculationResultsSec.getCalculationTime())

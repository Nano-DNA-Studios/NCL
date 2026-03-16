from ..CalculationResults import CalculationResults

class OrcaCalculationResults(CalculationResults):
    
    outputFilePath: str
    """The Path to the Calculations Output File"""
    
    def __init__(self, elapsed: float, status: str):
        super().__init__(elapsed, status)
    
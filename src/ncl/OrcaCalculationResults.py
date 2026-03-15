from .CalculationResults import CalculationResults

class OrcaCalculationResults(CalculationResults):
    
    outputFilePath: str
    
    def __init__(self, elapsed: float, status: str):
        super().__init__(elapsed, status)
    
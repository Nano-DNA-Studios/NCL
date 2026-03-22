from abc import ABC, abstractmethod

class ICalculation(ABC):
    
    @abstractmethod
    def calculate(self):
        """Runs the calculation, must be implemented by inherited class
        
        Returns :
            CalculationResult - Returns a Calculation Result Object, contains the path to the output file and common calculation statistics 
        """
        pass
    
    @abstractmethod
    def setup(self):
        """Organizes and sets up necessary resources for the calculation"""
        pass
    
    @abstractmethod
    def getInputFileName(self):
        """Gets the name of the Input file
        
        Returns :
            str - Name of the Output File with extension
        """
        pass
    
    @abstractmethod
    def getOutputFileName(self):
        """Gets the name of the Output file
        
        Returns :
            str - Name of the Output File with extension
        """
        pass
        
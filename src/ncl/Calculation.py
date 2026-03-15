import os
from .InputFile import InputFile
from .ICalculation import ICalculation

class Calculation(ICalculation):
    
    def __init__(self, inputFile : InputFile):
        
        if (not isinstance(inputFile, InputFile)):
            raise TypeError("The inputFile must be of type InputFile")
        
        self.baseCachePath = os.path.join(os.getcwd(), "Cache")
        self.inputFile = inputFile
    
    def calculate(self):
        raise NotImplementedError("Calculate function has not been implemented")
    
    def setup(self):
        if (not os.path.exists(self.baseCachePath)):
            os.mkdir(self.baseCachePath)
    
    def getInputFileName(self):
        return self.inputFile.name + self.inputFile.extension
    
    def getOutputFileName(self):
        return self.inputFile.name + ".out"
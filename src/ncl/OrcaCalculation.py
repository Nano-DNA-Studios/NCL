import os
from .Calculation import Calculation
from .InputFile import InputFile

class OrcaCalculation(Calculation):
    
    def __init__(self, inputFile : InputFile):
        super().__init__(inputFile)
        
        self.cachePath = os.path.join(self.baseCachePath, "Orca", inputFile.name)
        
    def calculate(self):
        self.setup()
        
        print(f"Running Calculation using the following Input File : \n {self.inputFile.build()}")
        
        raise NotImplemented("Running Orca Calculations Locally has not been implemented yet!")
    
    def setup(self):
        super().setup()
        
        if (not os.path.exists(self.cachePath)):
            os.makedirs(self.cachePath)
        
        self.inputFile.save(self.cachePath)    
       
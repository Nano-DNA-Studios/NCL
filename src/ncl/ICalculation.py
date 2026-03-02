import os
from abc import ABC, abstractmethod
from .InputFile import InputFile

class ICalculation(ABC):
    
    @abstractmethod
    def calculate(self):
        pass
    
    @abstractmethod
    def setup(self):
        pass
    
    @abstractmethod
    def getInputFileName(self):
        pass
    
    @abstractmethod
    def getOutputFileName(self):
        pass
        
        

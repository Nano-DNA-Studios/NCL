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
    
    def calculationTime(self, seconds: float):
        """Converts Calculation Time Seconds to Human Readable Clock Format

        ## Parameters : \n
            self - Default Parameter for the Class Instance \n
            seconds : int - Number of Seconds to Convert to Clock Format

        ## Returns : \n
            str - The time in a clock format (x days : y hours : z mins : a sec)
        """
        # Convert Seconds to Hours, Minutes, and Seconds
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        remainingSeconds = seconds % 60

        # Generate the Time String
        parts = []
        if days > 0:
            parts.append(f"{int(days)} day{'s' if days > 1 else ''}")
        if hours > 0:
            parts.append(f"{int(hours)} hour{'s' if hours > 1 else ''}")
        if minutes > 0:
            parts.append(f"{int(minutes)} minute{'s' if minutes > 1 else ''}")
        if remainingSeconds > 0:
            parts.append(
                f"{int(remainingSeconds)} second{'s' if remainingSeconds > 1 else ''}"
            )

        # Return the Time String
        return ", ".join(parts) if parts else "0 seconds"
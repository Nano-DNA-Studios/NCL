import os
import time
import shutil
import subprocess
from ..InputFile import InputFile
from ..Calculation import Calculation
from .OrcaCalculationResults import OrcaCalculationResults

class OrcaCalculation(Calculation):

    def __init__(self, inputFile: InputFile):
        super().__init__(inputFile)

        self.cachePath = os.path.join(self.baseCachePath, "Orca", inputFile.name)

    def calculate(self):
        """Runs the Orca Calculation through the Local Executable
        
        Returns : 
            OrcaCalculationResults - A Calculation Result Object with the path to the output file, calculation statistics and other Orca specific stats  
        """
        self.setup()

        print(
            f"Running Calculation using the following Input File : \n {self.inputFile.build()}"
        )

        fullCommand = f"cd {self.cachePath} && {self.getOrcaPath()} {self.getInputFileName()} > {self.getOutputFileName()}"

        start = time.time()

        try:
            subprocess.run(
                fullCommand,
                shell=True,
                stderr=subprocess.DEVNULL,
            )

        except:
            print(f"An Error Occured during the calculation")
            
            elapsed = time.time() - start
            
            return OrcaCalculationResults(elapsed, "Failure")
        
        elapsed = time.time() - start
        
        calculationResults = OrcaCalculationResults(elapsed, "Success")

        calculationResults.outputFilePath = os.path.join(self.cachePath, self.getOutputFileName())

        print(f"Calculation Finished! : {calculationResults.getCalculationTime()}")
        
        return calculationResults
        
    def setup(self):
        super().setup()

        if not os.path.exists(self.cachePath):
            os.makedirs(self.cachePath, exist_ok=True)

        self.inputFile.save(self.cachePath)
        
    def getOrcaPath(self):
        """Finds the path to the Orca Executable.
        
        Returns :
            str - The absolute path to the Orca Executable on the device
        """
        orcaPath = shutil.which("orca")

        if orcaPath is None:
            raise RuntimeError("Could not find Orca in the PATH.")

        return orcaPath
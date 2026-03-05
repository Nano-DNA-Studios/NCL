import os
import time
import shutil
import subprocess
from .InputFile import InputFile
from .Calculation import Calculation


class OrcaCalculation(Calculation):

    def __init__(self, inputFile: InputFile):
        super().__init__(inputFile)

        self.cachePath = os.path.join(self.baseCachePath, "Orca", inputFile.name)

    def calculate(self):
        self.setup()

        orcaPath = shutil.which("orca")

        if orcaPath is None:
            raise RuntimeError("Could not find Orca in the PATH.")
        
        print(
            f"Running Calculation using the following Input File : \n {self.inputFile.build()}"
        )

        fullCommand = f"cd {self.cachePath} && {orcaPath} {self.getInputFileName()} > {self.getOutputFileName()}"

        start = time.time()

        subprocess.run(
            fullCommand,
            shell=True,
            stderr=subprocess.DEVNULL,
        )

        elapsed = time.time() - start

        print(f"Calculation Finished! : {elapsed} seconds")

    def setup(self):
        super().setup()

        if not os.path.exists(self.cachePath):
            os.makedirs(self.cachePath)

        self.inputFile.save(self.cachePath)

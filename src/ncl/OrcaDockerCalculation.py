import subprocess
from .OrcaCalculation import OrcaCalculation
from .InputFile import InputFile

# Replace the subprocesses with an Actual Docker Object for more in depth and complex stuff
class OrcaDockerCalculation(OrcaCalculation):

    def __init__(self, inputFile: InputFile):
        """Constructor for OrcaDockerEngine

        Initializes a new Instance of the Engine. Used to run a Orca Calculation inside a Docker Container

        Parameters:
            calcFileName (str) - The name of the Calculation, used to name the Input file and Output file
            cachePath (str) - The path to the Cache Folder where the Input, Output and other Calculation files are outputted
        """
        super().__init__(inputFile)

        self.containerName = "ncrlorca"
        self.imageName = "mrdnalex/orca"

    def calculate(self):
        """calculate(self)

        Runs the Orca Calculation through a Docker Container and cleans itself up
        """
        super().setup()

        print(f"Running Calculation using the following Input File : \n {self.inputFile.build()}")

        fullCommand = f'docker run --name {self.containerName} -v "{self.cachePath}":/home/orca {self.imageName} sh -c "cd /home/orca && /Orca/orca {self.getInputFileName()} > {self.getOutputFileName()}"'

        self._remove()

        subprocess.run(
            fullCommand,
            shell=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )

        self._remove()
        
        print("Calculation Finished!")

    def _remove(self):
        """_remove(self)

        Stops and Removes the Docker Container if it's running
        """
        subprocess.run(
            f"docker kill {self.containerName}",
            shell=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run(
            f"docker rm {self.containerName}",
            shell=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )

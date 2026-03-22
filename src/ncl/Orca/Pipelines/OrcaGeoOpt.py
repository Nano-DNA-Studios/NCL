import os
import time
from ncl import Calculation, Molecule
from ncl.Orca import OrcaCalculation, OrcaCalculationResults, OrcaDockerCalculation, OrcaInputFile, OrcaOutputFile

class OrcaGeoOptCalculationResults(OrcaCalculationResults):
    
    initial: Molecule
    """The Initial Inputted Molecule Geometry """
    
    final: Molecule
    """The Final Optimized Molecule Geometry"""
    
    iterations: list[Molecule]
    """The Iterations of Molecules going through the Geometry Optimization starting with the initial and ending with the final"""
    
    def __init__(self, time: float, status: str):
            super().__init__(time, status)
    
class OrcaGeoOpt(Calculation):
    
    initialMolecule: Molecule
    """The Inputted Geometry of the Molecule"""
    
    iterations: list[Molecule]
    """The Iterations of Molecules going through the Geometry Optimization starting with the initialMolecule and ending with the finalMolecule"""
    
    method: str
    """Stores the Orca Calculation Method"""
    
    basis:str
    """Stores the Basis Set used for the Calculation"""
    
    extras: tuple[str, ...]
    """Stores extra Keywords and commands for the calculation""" 
    
    useDocker: bool
    """Toggle indicating to use the Orca Docker Image or the Local Orca Software"""
    
    def __init__(self, molecule: Molecule, method: str, basis: str, *extras: str, useDocker: bool = True):
        
        self.initialMolecule = molecule
        self.initialMolecule.name = self.initialMolecule.name + "-GeoOpt"
        
        self.method = method
        self.basis = basis
        self.extras = extras
        self.useDocker = useDocker
        self.iterations = []
        self.iterations.append(self.initialMolecule)
        
        super().__init__(self.getGeoOptInputFile(self.initialMolecule, 1))
        self.cachePath = os.path.join(self.baseCachePath, "Orca", self.initialMolecule.name)
        
    def setup(self):
        super().setup()
            
        if (not os.path.exists(self.cachePath)):
            os.mkdir(self.cachePath)
            
    def calculate(self):
        """Runs an Iterative Geometry Optimization on the selected molecule. It will repeatedly optimize the Molecule until it is mathematically Optimized
        
        Returns :
            OrcaGeoOptCalculationResults - Returns the Result of the Calculation with a few commonly accessed values
        """
        self.setup()
        
        index = 1
        optimized = False
        currentMolecule = self.initialMolecule
        start = time.time()
        
        print(f"Starting Geometry Optimization of Molecule {self.initialMolecule.name}")
        
        while (not optimized):
            index += 1
            
            # Run the Calculation
            calculation = OrcaDockerCalculation(self.inputFile) if self.useDocker else OrcaCalculation(self.inputFile)
            calculation.cachePath = os.path.join(self.cachePath, self.inputFile.name)
            result = calculation.calculate()
            
            # Get the latest Molecule and Append to the list
            optimizedMoleculePath = os.path.join(calculation.cachePath, calculation.inputFile.name + ".xyz")
            currentMolecule = Molecule(f"{self.initialMolecule.name}-{index}", optimizedMoleculePath)
            self.iterations.append(currentMolecule)
            
            # Check if Molecule is Optimized and Complete Calculation if so
            outputFile = OrcaOutputFile(result.outputFilePath)
            
            if (self.isOptimized(outputFile.IRFrequencies["Wavenumber"]) or result.status == "Failure"):
                optimized = True
                break
                
            # Create Input file for next Calculation Iteration
            self.inputFile = self.getGeoOptInputFile(currentMolecule, index)
            print(f"Starting Iteration {index} of Geometry Optimization")
            
        elapsed = time.time() - start
        
        # Create the Results object and return it
        calcResults = OrcaGeoOptCalculationResults(elapsed, result.status)
        calcResults.outputFilePath = result.outputFilePath
        calcResults.initial = self.initialMolecule
        calcResults.final = currentMolecule
        calcResults.iterations = self.iterations
        
        print(f"Geometry Optimization Finished! : {calcResults.getCalculationTime()}")
        
        return calcResults
    
    def getGeoOptInputFile(self, molecule: Molecule, index: int):
        """Creates a new Input File for the Geometry Optimization
        
        Parameters :
            molecule - The Molecule being placed into the Input File
            index - Integer index for the name of the Input File 
        
        Returns :
            OrcaInputFile - A new OrcaInputFile to be used for a GeoOpt Calculation
        """
        inputFile = OrcaInputFile(f"{self.initialMolecule.name}-{index}", molecule)
        inputFile.setGeometryOptimization(self.method, self.basis, *self.extras)
        inputFile.addRoute("FREQ")
        return inputFile
        
    def isOptimized(self, frequencies: list[float]) -> bool:
        """Checks if the Molecule has been Optimized using the Vibrational Frequencies. Returns a boolean indicating if Optimized (Fully Optimized = All Frequencies > 0)
        
        Parameters :
            self - Default Parameter for the Class Instance \n
            frequencies - A list of Vibrational Frequencies
        
        Returns :
            bool - True if Molecule is Optimized, False if not Optimized
        """
        for freq in frequencies:
            if freq < 0:
                return False

        return True

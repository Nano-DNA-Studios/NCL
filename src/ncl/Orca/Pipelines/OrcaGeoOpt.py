import os
from ncl import ICalculation, Molecule
from ncl.Orca import OrcaInputFile

class OrcaGeoOpt(ICalculation):
    
    initialMolecule: Molecule
    """The Inputted Geometry of the Molecule"""
    
    finalMolecule: Molecule
    """The Final Geometry of the Molecule once fully Optimized"""
    
    iterations: list[Molecule]
    """The Iterations of Molecules going through the Geometry Optimization starting with the initialMolecule and ending with the finalMolecule"""
    
    method: str
    
    basis:str
    
    
    
    
    def __init__(self, molecule: Molecule, method: str, basis: str, *extras: tuple[str, str]):
        
        self.initialMolecule = molecule
        self.method = method
        self.basis = basis
        self.extras = extras
        
        self.baseCachePath = os.path.join(os.getcwd(), "Cache")
        self.cachePath = os.path.join(self.baseCachePath, "Orca", self.initialMolecule.name)
        
        self.iterations = []
        self.iterations.append(self.initialMolecule)
    
    def setup(self):
        if (not os.path.exists(self.baseCachePath)):
            os.mkdir(self.baseCachePath)
    
    def calculate(self):
        
        # Need to create Input file variable
        # Need to create index
        index = 1
        optimized = False
        currentMolecule = self.initialMolecule
        inputFile = OrcaInputFile(f"{self.initialMolecule.name}-GeoOpt-{index}", currentMolecule)
        
        while (not optimized):
            
            inputFile = OrcaInputFile(f"{self.initialMolecule.name}-GeoOpt-{index}", currentMolecule)
            inputFile.setGeometryOptimization(self.method, self.basis, self.extras)
            
            
            
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    



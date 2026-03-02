from .InputFile import InputFile
from .Molecule import Molecule

class OrcaInputFile(InputFile):

    MOLECULE_INPUT: str = "* xyz 0 1 \n&{molecule}\n*"
    BASIC = "!&{calculation} &{basis} &{functional}"
    HARTREE_FOCK = "HF"

    def __init__(self, name : str,  molecule: Molecule):
        super().__init__(name, ".inp")

        if (not isinstance(molecule, Molecule)):
            raise TypeError("The Molecule passed in is not of Type Molecule!")
        
        self.molecule = molecule
        self.addStructure(self.MOLECULE_INPUT, molecule=molecule.getContent())
    
    def setHartreeFock(self, basis : str, functional : str):
        
        if (not isinstance(basis, str)):
            raise TypeError("The basis must be a string")
        
        if (not isinstance(functional, str)):
            raise TypeError("The functional must be a string")
        
        if len(basis.strip()) == 0:
            raise ValueError("The basis cannot be empty")
        
        if len(functional.strip()) == 0:
            raise ValueError("The basis cannot be empty")
        
        self.setHeader(self.BASIC, basis = basis, functional = functional, calculation = "HF")

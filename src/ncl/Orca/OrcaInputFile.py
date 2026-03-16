from ..Molecule import Molecule
from ..InputFile import InputFile

class OrcaInputFile(InputFile):

    def __init__(self, name : str, molecule: Molecule):
        super().__init__(name, ".inp", molecule)

        self.keywordCommands: list[str] = []
        self.blocks: dict[str, str] = {}
        
    def addRoute(self, command: str):
        """Adds a single command to the route section (e.g., 'Opt')."""
        if not isinstance(command, str) or len(command.strip()) == 0:
            raise ValueError("Command must be a non-empty string")
        self.keywordCommands.append(command.strip())
        
    def addBlock(self, block_name: str, content: str):
        """Adds a detailed block (e.g., '%pal nprocs 8 end')."""
        if not isinstance(block_name, str) or not isinstance(content, str):
            raise TypeError("Block name and content must be strings")
        self.blocks[block_name.strip()] = content.strip()
        
    
    def setMethod(self, method: str, basis: str, *extras: str):
        """Helper to quickly set a generic calculation method."""
        self.keywordCommands.clear() # Reset in case they call it twice
        self.addRoute(method.upper())
        self.addRoute(basis)
        for extra in extras:
            self.addRoute(extra)
        
    def setHartreeFock(self, basis: str):
        """Helper specifically for Hartree-Fock calculations."""
        if not isinstance(basis, str) or len(basis.strip()) == 0:
            raise ValueError("The basis must be a non-empty string")
        
        self.setMethod("HF", basis)

    def setParallelProcessing(self, cores: int):
        """Helper to easily add the parallel processing block."""
        if cores > 1:
            self.addBlock("pal", f"nprocs {cores}")
            
    def setGeometryOptimization(self, method: str, basis: str, *extras: str):
        """Helper specifically for Geometry Optimization calculation."""
        if not isinstance(method, str) or len(method.strip()) == 0:
            raise ValueError("The method must be a non-empty string")
            
        if not isinstance(basis, str) or len(basis.strip()) == 0:
            raise ValueError("The basis must be a non-empty string")
        
        self.setMethod(method, basis, "OPT", *extras)
    
    def setFrequencyCalculation(self, method: str, basis: str, *extras: str):
        """Helper specifically for Frequency calculation."""
        if not isinstance(method, str) or len(method.strip()) == 0:
            raise ValueError("The method must be a non-empty string")
            
        if not isinstance(basis, str) or len(basis.strip()) == 0:
            raise ValueError("The basis must be a non-empty string")
        
        self.setMethod(method, basis, "FREQ", *extras)
        
    def setSinglePointEnergy(self, method: str, basis: str, *extras: str):
        """Helper specifically for Single Point Energy calculation."""
        if not isinstance(method, str) or len(method.strip()) == 0:
            raise ValueError("The method must be a non-empty string")
            
        if not isinstance(basis, str) or len(basis.strip()) == 0:
            raise ValueError("The basis must be a non-empty string")
        
        self.setMethod(method, basis, *extras)
            
    def build(self) -> str:
        lines = []
        
        # 1. Build the Keyword Command Line
        if self.keywordCommands:
            keyworkLine = "! " + " ".join(self.keywordCommands)
            lines.append(keyworkLine)
            
        # 2. Build the Blocks Section (%...)
        for name, content in self.blocks.items():
            lines.append(f"%{name}")
            lines.append(content)
            lines.append("end")
            
        # 3. Build the Coordinate Section (* xyz 0 1 ...)
        lines.append(f"* xyz {self.molecule.charge} {self.molecule.multiplicity}")
        lines.append(self.molecule.getContent())
        lines.append("*")
        
        return "\n".join(lines)

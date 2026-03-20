import os
import pandas as pd

class Molecule:

    def __init__(self, name: str, filePath: str, charge: int = 0, mult: int = 1):
        
        if (not isinstance(name, str)):
            raise TypeError("The name of the Molecule must be a string")
        
        if (not isinstance(filePath, str)):
            raise TypeError("The filePath of the Molecule must be a string")
        
        if len(name.strip()) == 0:
            raise ValueError("The name cannot be empty")
        
        if len(filePath.strip()) == 0:
            raise ValueError("The filePath cannot be empty")
        
        if (not os.path.exists(filePath)):
            raise FileNotFoundError(f"The file located at {filePath} does not exist")
        
        self.name: str = name
        self.filePath: str = filePath
        self.positions: pd.DataFrame = self._readXYZ(filePath)
        self.charge = charge
        self.multiplicity = mult

    def _readXYZ(self, filePath: str):
        """Extracts the Atom type and XYZ Coordinates from a `.xyz` file, returns the structure as a Pandas Dataframe

        Parameters :
            filePath (str) - The path to the XYZ File to load

        Returns :
            pd.Dataframe - Pandas Dataframe containing the following Columns, [Atom, X, Y, Z], where XYZ are the Positions
        """

        if not os.path.exists(filePath):
            raise FileNotFoundError(f"The file located at {filePath} does not exist ({os.getcwd()})")

        return pd.read_csv(
            filePath,
            sep=r"\s+",
            skiprows=2,
            names=["Atom", "X", "Y", "Z"],
            engine="python",
        )
        
    def getContent(self) -> str:
        """Gets the Atomic Element and Atomic Coordinates of the molecule in string format
        
        Returns :
            str - The Atomic Element and Coordinates in a large string in the following format [Element X Y Z]
        """
        return self.positions.to_string(header=False, index=False)
        
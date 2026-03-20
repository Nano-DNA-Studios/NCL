import os
import numpy as np
from numpy.random import random
import pandas as pd
from .Constants import CovalentRadiiConstants, AtomicMassConstants

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
        self.atomCount: int = len(self.positions)
        self.bonds = self.getBonds()
        self.charge = charge
        self.multiplicity = mult

    def _readXYZ(self, filePath: str, unsorted: bool = False):
        """Reads the Contents of an XYZ file and returns the Atom Coordinates as a DataFrame (Default Behavior is a Sorted)

        Parameters :
            filePath (str) - The path to the XYZ File to load
            unsorted (bool = False) - Toogle to return the XYZ File with it's atoms Sorted from Heaviest to Lightest element

        Returns :
            pd.Dataframe - Pandas Dataframe containing the following Columns, [Atom, X, Y, Z], where XYZ are the Positions
        """

        if not os.path.exists(filePath):
            raise FileNotFoundError(f"The file located at {filePath} does not exist ({os.getcwd()})")

        dataframe = pd.read_csv(
                    filePath,
                    sep=r"\s+",
                    skiprows=2,
                    names=["Atom", "X", "Y", "Z"],
                    engine="python",
                )

        if (unsorted):
            return dataframe
        else:
            return self.sortAtomDataFrame(dataframe)
            
    def getContent(self) -> str:
        """Gets the Atomic Element and Atomic Coordinates of the molecule in string format
        
        Returns :
            str - The Atomic Element and Coordinates in a large string in the following format [Element X Y Z]
        """
        return self.positions.to_string(header=False, index=False)
    
    def getBonds(self):
        """Generates the Bonds DataFrame for the Molecule, fills the DataFrame with Atomic indices in the Molecule, their atomic symbol, indices of the atoms they are bonded to and the distances of those bonds

        Returns :
            pandas.Dataframe - Pandas Dataframe describing the Bond Arrangements
        """
        # Pre initialize variables
        atTypes = self.positions["Atom"].values
        index = [i for i in range(self.atomCount)]
        bonds = [[] for i in range(self.atomCount)]
        bondsDistance = [[] for i in range(self.atomCount)]

        # Get the Bonds and save to Array
        for i in range(self.atomCount):
            radii1 = CovalentRadiiConstants[atTypes[i]]
            for j in range(i + 1, self.atomCount):
                radii2 = CovalentRadiiConstants[atTypes[j]]
                thresh = 1.1 * (radii1 + radii2)
                dist = self.getBondLength(i, j)
                if dist < thresh:
                    bonds[i].append(j)
                    bonds[j].append(i)

        # Get Bond Distances
        for i in range(self.atomCount):
            for j in bonds[i]:
                bondsDistance[i].append(self.getBondLength(i, j))

        bondDF = pd.DataFrame(
            {
                "Index": index,
                "Atom": atTypes,
                "Bonds": bonds,
                "Bond Distance": bondsDistance
            }
        )
        
        bondDF["Rotatable"] = self.getRotatableBonds(bondDF)
        
        return bondDF
        
    def getRotatableBonds(self, bondDF: pd.DataFrame) -> list[bool]:
        """Gets the rotatable bonds in the Molecule as a Boolean List. Rotatable bonds are not completely accurate, relies on finding a loop in the molecule (Double and Tripple bonds are still considered rotatable in this case so beware)

        Parameters:
            bondDF (pandas.DataFrame) - DataFrame containing Molecule Bond Information

        Returns : 
            list[bool] - List of Booleans indecating if a Bond is rotatable based on a looping rule
        """
        # TODO: Will need to Factor in Double Bonds in the Future

        rotatableBonds: list[list[bool]] = []

        for i in range(self.atomCount):
            bonds = bondDF["Bonds"][i]
            rotatableList: list[bool] = []

            for j in bonds:
                atoms: list[int] = self.getAllAtomsAfterBond(i, j, bondDF)

                # Rules that determine if the Bond is Rotatable TODO: Expand to factor in double bonds and more rules
                rotatableList.append(not i in atoms)
                    
            rotatableBonds.append(rotatableList)

        return rotatableBonds
    
    def getAllAtomsAfterBond(self, atomIndex1: int, atomIndex2: int, bondDF: pd.DataFrame) -> list[int]:
        """Recusrsively Searches through all Atoms in the Molecule present after the specified bond

        Parameters : 
            atomIndex1 (int) - Index of the First Atom
            atomIndex2 (int) - Index of the Second Atom
            bondDF (pandas.DataFrame) - DataFrame containing Molecule Bond Information

        Returns :
            list[int] - List of the index of each Atom present after the bond
        """
        if (atomIndex2 not in bondDF["Bonds"][atomIndex1]):
            raise Exception("These Atoms are not Bonded Together")

        return self.branchSearch(bondDF, atomIndex2, [], atomIndex1)

    def branchSearch(self, bondDF: pd.DataFrame, currentIndex: int, atoms: list[int] = None, ignoreIndex: int = None) -> list[int]:
        """Recursively Searches through all Atoms in the Molecule

        Parameters :
            bondDF (pandas.DataFrame) - DataFrame containing Molecule Bond Information
            currentIndex (int) - Index of the Current Atom in the recursive search
            atoms (list[int]) - List of Atoms previously visited in the Branch Search
            ignoreIndex (int) - Index of the Molecule to ignore in the Search (Often just the Current index)

        Returns : 
            list[int] - List of the Atoms in the Molecule present after the specified bond
        """
        bonds: list[int] = bondDF["Bonds"][currentIndex]

        for i in bonds:
            if i == ignoreIndex:
                continue

            if i not in atoms:
                atoms.append(i)
                self.branchSearch(bondDF, i, atoms, currentIndex)

        return atoms
        
    def getBondLength(self, atomIndex1: int, atomIndex2: int):
        """Gets the Bond Length between 2 Atoms

        Parameters : 
            atomIndex1 (int) - Index of the First Atom
            atomIndex2 (int) - Index of the Second Atom

        Returns : 
            float - Distance between the 2 Atoms in Angstroms
        """
        vector = self.getXYZCoordinate(atomIndex1) - self.getXYZCoordinate(atomIndex2)
        return np.linalg.norm(vector)
    
    def getXYZCoordinate(self, atomIndex: int):
        """Gets a Numpy Array of the XYZ Coordinates of the Indexed Atom
        
        Returns a Numpy Array with the XYZ Position of the Specified Atom

        Parameters :
            atomIndex (int) - Index of the Atom in the Molecule

        Returns :
            NDArray[float] - Numpy Array containing the XYZ Coordinates of the Atom
        """
        return np.array(self.positions.iloc[atomIndex, slice(1, 4)], dtype=float)
    
    def sortAtomDataFrame(self, dataFrame: pd.DataFrame):
        """Sorts the Molecules Atoms Data Frame by ordering the Atoms from Heaviest Molecular Weight to Lowest

        Parameters :
            dataFrame (pandas.DataFrame) - The XYZ Position DataFrame to Sort

        Returns : 
            pandas.DataFrame - The DataFrame with Atom Positions sorted from Highest to Lowest Molecular Weight
        """
        # Create a duplicate of the DataFrame
        sortedDataFrame = dataFrame.copy()

        atoms = []

        for i in range(len(dataFrame["Atom"].values)):
            atoms.append([i, AtomicMassConstants[dataFrame["Atom"][i]]])

        # Sort atoms by atomic mass in descending order
        sortedAtoms = sorted(atoms, key=lambda x: x[1], reverse=True)

        # Extract the sorted indices and reindex the original Dataframe
        sortedIndices = [atom[0] for atom in sortedAtoms]
        sortedDataFrame = dataFrame.iloc[sortedIndices]

        # Replace rows in the duplicate DataFrame using the sorted indices
        for newIndex, (originalIndex, _) in enumerate(sortedAtoms):
            sortedDataFrame.iloc[newIndex] = dataFrame.iloc[originalIndex]

        # Resets the Now Sorted indexes so that they properly increment
        sortedDataFrame.reset_index(drop=True, inplace=True)

        return sortedDataFrame
    
    def generatePerpendicularVector(self, vector: np.ndarray) -> np.ndarray:
        """Generates a Perpendicular Vector to the Vector Provided

        Parameters :
            vector (np.ndarray) - Numpy Array of the Vector to Generate the Perpendicular Vector from

        Returns :
            np.ndarray - Vector that is Perpendicular to the one inputted
        """
        # Check if the input vector is not zero
        if np.linalg.norm(vector) == 0:
            raise ValueError("The input vector cannot be the zero vector")

        # Create a second vector which is not parallel to the input vector
        if vector[0] == 0:
            w = np.array(
                [1, 0, 0]
            )  # Choose a simple vector if the first element is zero
        else:
            w = np.array(
                [vector[1], -vector[0], 0]
            )  # This ensures the vector is not parallel

        # Compute the cross product
        crossProduct = np.cross(vector, w)

        # Normalize the cross product
        norm = np.linalg.norm(crossProduct)
        if norm == 0:
            raise ValueError(
                "The cross product resulted in a zero vector, which should not happen"
            )

        normalizedVector = crossProduct / norm

        return normalizedVector

    def rotateBond(self, atomIndex1: int, atomIndex2: int, radians: float):
        """Rotates a Bond in the Molecule by the Specified Radians

        Parameters : 
            atomIndex1 (int) - Index of the First Atom in the Bond \n
            atomIndex2 (int) - Index of the Second Atom in the Bond \n
            radians (float) - Radians to Rotate the Bond and all Atoms proceeding it
        """

        atomIndexes: list[int] = self.getAllAtomsAfterBond(atomIndex1, atomIndex2, self.bonds)
        atomPositions: np.ndarray = np.array(
            self.getXYZCoordinate(atomIndexes[0]) - self.getXYZCoordinate(atomIndex2)
        )

        for i in range(1, len(atomIndexes)):
            atomPositions = np.vstack(
                (
                    atomPositions,
                    self.getXYZCoordinate(atomIndexes[i])
                    - self.getXYZCoordinate(atomIndex2),
                )
            )

        zVector = self.getXYZCoordinate(atomIndex2) - self.getXYZCoordinate(atomIndex1)
        zVector = zVector / np.linalg.norm(zVector)

        xVector = self.generatePerpendicularVector(zVector)

        yVector = np.cross(zVector, xVector)
        yVector = yVector / np.linalg.norm(yVector)

        originalAxes = np.array(
            [
                xVector,  # Original X-axis
                yVector,  # Original Y-axis
                zVector,  # Original Z-axis
            ]
        )

        # Define rotation matrix around Z-axis by given radians
        cosTheta = np.cos(radians)
        sinTheta = np.sin(radians)
        zRotationMatrix = np.array(
            [[cosTheta, -sinTheta, 0], [sinTheta, cosTheta, 0], [0, 0, 1]]
        )

        # Combine the transformations to find the full rotation matrix
        rotationBasis = originalAxes.T
        rotationMatrix = rotationBasis @ zRotationMatrix @ np.linalg.inv(rotationBasis)

        # Apply the rotation to all atom positions
        rotatedAtoms = atomPositions @ rotationMatrix.T

        # Update atom coordinates in the original structure
        for i, atomIndex in enumerate(atomIndexes):
            newPosition = rotatedAtoms[i] + self.getXYZCoordinate(atomIndex2)
            self.positions.loc[atomIndex, "X"] = newPosition[0]
            self.positions.loc[atomIndex, "Y"] = newPosition[1]
            self.positions.loc[atomIndex, "Z"] = newPosition[2]
    
    def getDihedralAngle(
        self, atomIndex1: int, atomIndex2: int, atomIndex3: int, atomIndex4: int
    ) -> float:
        """Gets the Dihedral Angle in Degrees between 4 Atoms in the Molecule. (Gets the Angle between 2 vectors represented by bonds)

        Parameters :
            atomIndex1 (int) - Index of the First Atom 
            atomIndex2 (int) - Index of the Second Atom 
            atomIndex3 (int) - Index of the Third Atom 
            atomIndex4 (int) - Index of the Fourth Atom

        Returns :
            float - Dihdral Angle in Degrees between 2 Bonds or 4 Atoms
        """
        # Get the position of the Atoms
        atom1Pos = self.getXYZCoordinate(atomIndex1)
        atom2Pos = self.getXYZCoordinate(atomIndex2)
        atom3Pos = self.getXYZCoordinate(atomIndex3)
        atom4Pos = self.getXYZCoordinate(atomIndex4)

        # Get the Vectors between each atom
        v21 = atom2Pos - atom1Pos
        v32 = atom3Pos - atom2Pos
        v43 = atom4Pos - atom3Pos

        # Calculate the Dihedral Angles
        v1 = np.cross(v21, v32)
        v1 = v1 / np.linalg.norm(v1)
        v2 = np.cross(v43, v32)
        v2 = v2 / np.linalg.norm(v2)
        m1 = np.cross(v1, v32)
        m1 = m1 / np.linalg.norm(m1)
        x = np.dot(v1, v2)
        y = np.dot(m1, v2)
        chi = np.arctan2(y, x)
        chi = -180.0 - 180.0 * chi / np.pi
        if chi < -180.0:
            chi = chi + 360.0
        return chi

    def getAngleBetweenAtoms(self, atomIndex1: int, atomIndex2: int, atomIndex3: int):
        """Gets the Angle between 3 atoms in Degrees
        
        Parameters :
            atomIndex1 (int) - Index of the First Atom 
            atomIndex2 (int) - Index of the Second Atom, is the commonly shared Atom 
            atomIndex3 (int) - Index of the Third Atom 

        Returns :
            float - Angle between the bonded atoms in Degrees
        """
        # Get Atom Positions
        atom1Pos = self.getXYZCoordinate(atomIndex1)
        atom2Pos = self.getXYZCoordinate(atomIndex2)
        atom3Pos = self.getXYZCoordinate(atomIndex3)

        # Get Normalized Vectors
        v1 = atom1Pos - atom2Pos
        v1 = v1 / np.linalg.norm(v1)
        v2 = atom3Pos - atom2Pos
        v2 = v2 / np.linalg.norm(v2)

        # Return the Angle between the Vectors aka between Atoms
        return (180 / np.pi) * np.acos(np.dot(v1, v2))
    
    def getDihedralAtomChain(self, atomChain: list[int], depth: int = 0):
        """Recursively searches for a atom chain of length 4 to calculate the Dihedral angle

        Parameters :
            atomChain (list[int]) - List of Atoms indices that are in the Chain
            depth (int) - The Depth of the Recursive Search

        Returns : 
            list[int] - The Dihedral Atom chain list. Is of length 4
        """
        # Grab Bonds and Sort by incrementing index
        bonds: list[int] = self.bonds["Bonds"][atomChain[depth]]
        bonds.sort()

        for i in bonds:
            if len(atomChain) == 4:
                return atomChain

            if i in atomChain:
                continue

            currentAtomBonds: list[int] = self.bonds["Bonds"][i]

            # Skip if the Number of Bonds that the Current Atom has is Only one, Unless it is going to be the Last Atom in the Chain
            if len(currentAtomBonds) == 1 and (not len(atomChain) == 3):
                continue

            atomChain.append(i)
            
            self.getDihedralAtomChain(atomChain, depth + 1)

        return atomChain
    
    def getMolecularWeight(self) -> float:
        """Gets the Molecular Weight of the Molecule in grams/mol (g/mol)

        Returns :
            float - The Molecular Weight of the Molecule in g/mol
        """
        mw = 0

        for i in range(self.atomCount):
            mw += AtomicMassConstants[self.positions["Atom"][i]]

        return mw
    
    def createZMatrixFile(self):
        """Converts the Molecules info from XYZ Format to Z Matrix Format as a list of strings

        Returns :
            list[str] - List of Lines in the Z Matrix File
        """
        # Create an Array Reprensenting the File, First line is Number of Atoms, Second is the Name of the Molecule
        zMatrix: list[str] = []
        zMatrix.append(f"{self.atomCount}")
        zMatrix.append(self.name)

        # Loop through all the Atoms
        for i in range(self.atomCount):

            # Create an Atom Chain starting with the Current Atom
            atomChain = self.getDihedralAtomChain([i])

            # If the Chain hasn't reached 4 add Random Atoms until we reach 4
            while len(atomChain) < 4:
                randomAtom = random.randint(0, self.atomCount - 1)
                if randomAtom not in atomChain:
                    atomChain.append(randomAtom)

            # Save the Indexes to Variables
            j = atomChain[1]
            k = atomChain[2]
            l = atomChain[3]

            # Cache the Z Matrix Variables
            atomSymbol = self.positions["Atom"][i]
            radius = self.getBondLength(i, j)
            angle = self.getAngleBetweenAtoms(i, j, k)
            dihedralAngle = self.getDihedralAngle(i, j, k, l)

            # Check if First Atom, Only Append symbol
            if i == 0:
                zMatrix.append(f"{atomSymbol}")
                continue

            # Check if Second Atom, Append Symbol and Distance from Next Closest Atom
            if i == 1:
                zMatrix.append(f"{atomSymbol} {j+1} {radius}")
                continue

            # Check if Third Atom, Append Symbol, Distance and Angle
            if i == 2:
                zMatrix.append(f"{atomSymbol} {j+1} {radius} {k+1} {angle}")
                continue

            # Append Symbol, Distance, Angle and Dihedral Angle
            zMatrix.append(
                f"{atomSymbol} {j+1} {radius} {k+1} {angle} {l+1} {dihedralAngle}"
            )

        return zMatrix
    
    def displayZMatrix(self):
        """Displays the Molecules Atoms info in Z Matrix Format"""
        zMatrix = self.createZMatrixFile()
        for i in zMatrix:
            print(i)
            
    def displayBondGraph(self):
        """Prints the Bond graph to the Terminal. Displays the index of atoms that are bonded to the displayed index"""
        # Display Title Header
        print("   %s\n" % (self.name), end="")

        for i in range(self.atomCount):
            # Get Index and Atom Symbol
            index = self.bonds["Index"][i]
            atom = self.bonds["Atom"][i]
            rotatable = self.bonds["Rotatable"]

            # Create the String for Bonds
            bonds = ""
            for j in self.bonds["Bonds"][i]:
                bonds += str(j + 1) + " "

            # Create String for Bond Distance
            bondDist = ""
            for j in self.bonds["Bond Distance"][i]:
                bondDist += "%.3fÅ " % j

            # Create String for Rotatable Bonds
            rotatable = ""
            for j in self.bonds["Rotatable"][i]:
                if j:
                    rotatable += "T "
                else:
                    rotatable += "F "

            # Print Line to Screen
            print(
                " %4i   %-2s - %s    %4s  %2s"
                % (index + 1, atom, bonds, bondDist, rotatable)
            )
import re
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class OrcaOutputFile:
    """Represents an Orca Output File, used to Parse information from the Output File"""
    
    # TODO: Eventually convert this to using the .property.txt file
    
    def __init__(self, filePath: str):
        """Initialize OrcaOutput with ORCA output file path and extract all data."""
        # Store file path and read contents
        self.filePath = filePath
        with open(self.filePath, "r") as file:
            self.lines = file.readlines()

        # Extract filename without path/extension using regex
        self.name =  os.path.splitext(os.path.basename(self.filePath))[0]

        # Determine calculation types (FREQ, NMR, OPT, GOAT)
        self.calculationTypes = self.getCalculationTypes()

        # Extract basic calculation data
        self.atomNum = self.getNumberOfAtoms()
        self.SCFEnergies = self.getSCFEnergies()
        self.finalTimings = self.getFinalTimings()
        self.totalTime = self.getTotalTime()
        self.mayerPopulation = self.getMayerPopulation()
        self.loedwin = self.getLoewdinCharges()
        self.dipole = self.getDipoleVector()
        self.absolutedipole = self.getDipoleMagnitude()
        self.energy = self.getFinalEnergy()

        # Extract calculation-specific data based on type
        self.vibrationalFrequencies = self.getVibrationalFrequencies() if "FREQ" in self.calculationTypes else None
        self.normalModes = self.getNormalModes() if "FREQ" in self.calculationTypes else None
        self.IRFrequencies = self.getIRFrequencies() if "FREQ" in self.calculationTypes else None
        self.totalThermalEnergy = self.getTotalThermalEnergy() if "FREQ" in self.calculationTypes else None
        self.totalEnthalpy = self.getTotalEnthalpy() if "FREQ" in self.calculationTypes else None
        self.thermalEnthalpyCorrection = self.getThermalEnthalpyCorrection() if "FREQ" in self.calculationTypes else None
        self.chemicalShifts = self.getChemicalShifts() if "NMR" in self.calculationTypes else None
        self.conformers = self.getConformerInfo() if "GOAT" in self.calculationTypes else None
        self.GOATSummary = self.getGoatSummary() if "GOAT" in self.calculationTypes else None
    
    def readXYZFile(self, path: str) -> pd.DataFrame:
        """Read XYZ format atomic coordinates."""
        return pd.read_csv(path, sep=r"\s+", skiprows=1, names=["Atom", "X", "Y", "Z"], engine="python")
    
    def getCalculationTypes(self) -> list[str]:
        """Determine types of calculations in output file."""
        calculationTypes = []

        for line in self.lines:
            if "VIBRATIONAL FREQUENCIES" in line:
                calculationTypes.append("FREQ") if not "FREQ" in calculationTypes else None
            elif "CHEMICAL SHIELDINGS (ppm)" in line:
                calculationTypes.append("NMR") if not "NMR" in calculationTypes else None
            elif "GEOMETRY OPTIMIZATION" in line:
                calculationTypes.append("OPT") if not "OPT" in calculationTypes else None
            elif "GOAT Global Iter" in line:
                calculationTypes.append("GOAT") if not "GOAT" in calculationTypes else None

        return calculationTypes

    def getFinalTimings(self) -> pd.DataFrame:
        """Extract computational timing information."""
        for i, line in enumerate(self.lines[-20:]):
            if line.strip() == "Timings for individual modules:":
                startIndex = i + 2
                timeLines = self.lines[-20:][startIndex:-2]

                # Process timing data into a DataFrame
                df = pd.DataFrame([line.split("...") for line in timeLines], columns=["Timing", "Time"])
                df[["Time", "B"]] = df["Time"].str.split("sec", n=1, expand=True)
                return df.drop(["B"], axis=1)

    def getTotalTime(self) -> float:
        """Extracts the total calculation time in seconds"""
        for i, line in enumerate(self.lines[-5:]):
            if (line.strip().startswith("TOTAL RUN TIME")):
                parts = line.split()

                # Extract Values
                days = int(parts[3])
                hours = int(parts[5])
                minutes = int(parts[7])
                seconds = int(parts[9])
                msec = int(parts[11])
                
                # Convert all units to total seconds
                return (days * 86400) + (hours * 3600) + (minutes * 60) + seconds + (msec / 1000.0)
            
        return 0.0

    def getFinalEnergy(self) -> float:
        """Extract final single-point energy from output."""
        for line in self.lines:
            if line.strip().startswith("FINAL SINGLE POINT ENERGY"):
                return float(line.split()[-1])
                    
    def getSCFEnergies(self) -> list:
        """Extract SCF iteration energies and convergence data."""
        SCFEnergies = []

        # Look for SCF energy blocks
        for i, line in enumerate(self.lines):
            # Look for headers indicating SCF energy sections
            if "TOTAL SCF ENERGY" in line or "FINAL SINGLE POINT ENERGY" in line:
                # Skip header lines to get to actual energy value
                for j in range(i + 1, min(i + 5, len(self.lines))):
                    if "Total Energy" in self.lines[j]:
                        # Extract energy value
                        energy = float(self.lines[j].split()[-2])
                        SCFEnergies.append(energy)
                        break
                    elif any(char.isdigit() for char in self.lines[j]):
                        # Direct energy value line
                        energy = float(self.lines[j].split()[-2])
                        SCFEnergies.append(energy)
                        break

        return SCFEnergies

    def getMayerPopulation(self) -> list:
        """Extract Mayer population analysis data for atomic properties."""
        # Get total number of atoms
        for line in self.lines:
            if line.strip().startswith("Number of atoms"):
                atomCount = int(line.split()[-1])

        mayerPopulations = []
        # Look for Mayer population blocks
        for i, line in enumerate(self.lines):
            if line.strip() == "ATOM       NA         ZA         QA         VA         BVA        FA":
                startIndex = i + 1
                endIndex = i + atomCount + 1
                mayerLines = self.lines[startIndex:endIndex]

                # Convert to DataFrame with atomic properties
                df = pd.DataFrame(
                    [line.split()[1:8] for line in mayerLines],
                    columns=["ATOM", "NA", "ZA", "QA", "VA", "BVA", "FA"],
                )
                # Convert numeric columns
                df[["NA", "ZA", "QA", "VA", "BVA", "FA"]] = df[["NA", "ZA", "QA", "VA", "BVA", "FA"]].astype(float)
                mayerPopulations.append(df)

        return mayerPopulations

    def getDipoleVector(self) -> tuple:
        """Extract x, y, z components of dipole moment vector."""
        for line in self.lines:
            if line.strip().startswith("Total Dipole Moment"):
                return tuple(map(float, line.split()[4:]))  # Convert to floats

    def getDipoleMagnitude(self) -> float:
        """Extract magnitude of total dipole moment."""
        for line in self.lines:
            if line.strip().startswith("Magnitude (a.u.)"):
                return float(line.split()[3])

    def getVibrationalFrequencies(self) -> pd.DataFrame:
        """Extract vibrational frequencies from frequency calculation."""
        freqs = []
        for i, line in enumerate(self.lines):
            if "VIBRATIONAL FREQUENCIES" in line:
                startIdx = i + 5  # Skip header lines
                # Process each frequency line
                while self.lines[startIdx].strip():
                    parts = self.lines[startIdx].split()
                    if len(parts) >= 2:
                        freqs.append(
                            {
                                "Mode": int(parts[0].strip(":")),
                                "Wavenumber": float(parts[1]),
                            }
                        )
                    startIdx += 1

        # Return empty DataFrame if no frequencies found
        if len(freqs) == 0:
            return pd.DataFrame(columns=["Mode", "Wavenumber"])
        return pd.DataFrame(freqs)

    def getGibbsEnergy(self) -> tuple:
        """Extract Gibbs free energy and units."""
        for i, line in enumerate(self.lines):
            if line.strip()[0:23] == "Final Gibbs free energy":
                gibbs = float(re.search(r"-?\d+\.\d+", line).group())
                unit = re.search(r"\b\w+\b$", line).group()
                return gibbs, unit
            
    def getSolvationEnergy(self) -> float:
        """Extract solvation energy (Eh) from output

        ## Parameters : \n
            self : OrcaOutput - Default Parameter for the Class Instance

        ## Returns : \n
            float - Solvation energy of the solute in the specified solvent (Eh)
        """
        for line in self.lines:
            if "Gsolv" in line: 
                solvationEnergy = float(line.strip()[29:-9])
        return solvationEnergy

    def getConformerInfo(self) -> pd.DataFrame:
        """Extract conformer energies and populations."""
        conformers = []
        for i, line in enumerate(self.lines):
            if "# Final ensemble info #" in line:
                startIdx = i + 2  # Skip header
                while "------" not in self.lines[startIdx]:
                    startIdx += 1
                startIdx += 1  # Skip separator line

                while self.lines[startIdx].strip() and not "Conformers below" in self.lines[startIdx]:
                    parts = self.lines[startIdx].split()
                    if len(parts) >= 5:
                        conformers.append(
                            {
                                "conformer": int(parts[0]),
                                "energy": float(parts[1]),
                                "degeneracy": int(parts[2]),
                                "totalPercent": float(parts[3]),
                                "cumulativePercent": float(parts[4]),
                            }
                        )
                    startIdx += 1

        return pd.DataFrame(conformers)

    def getGoatSummary(self) -> dict:
        """Extract GOAT calculation summary."""
        summary = {}
        for line in self.lines:
            if "Conformers below" in line:
                summary["conformersBelow3KCal"] = int(line.split(":")[1])
            elif "Lowest energy conformer" in line:
                summary["lowestEnergy"] = float(line.split(":")[1].split()[0])
            elif "Sconf at" in line:
                summary["sconf"] = float(line.split(":")[1].split()[0])
            elif "Gconf at" in line:
                summary["gconf"] = float(line.split(":")[1].split()[0])
        return summary

    def getIRFrequencies(self) -> pd.DataFrame:
        """Extract IR frequencies and intensities."""
        freqs = []
        for i, line in enumerate(self.lines):
            if "IR SPECTRUM" in line:
                startIdx = i + 4  # Skip header lines
                while self.lines[startIdx].strip():
                    parts = self.lines[startIdx].split()
                    if len(parts) >= 7:  # Mode, freq, eps, Int, T**2, TX, TY, TZ
                        freqs.append(
                            {
                                "Mode": int(parts[0].strip(":")),
                                "Wavenumber": float(parts[1]),
                                "IRIntensity": float(parts[3]),  # km/mol
                            }
                        )
                    startIdx += 1
        return pd.DataFrame(freqs)

    def getChemicalShifts(self) -> pd.DataFrame:
        """Extract NMR chemical shifts."""
        shifts = []
        for i, line in enumerate(self.lines):
            if "CHEMICAL SHIELDING SUMMARY (ppm)" in line:
                startIdx = i + 6
                while self.lines[startIdx].strip():
                    parts = self.lines[startIdx].split()
                    if len(parts) >= 4:
                        shifts.append(
                            {
                                "atom": parts[0],
                                "nucleus": parts[1],
                                "isotropic": float(parts[2]),
                                "anisotropic": float(parts[3]),
                            }
                        )
                    startIdx += 1
        return pd.DataFrame(shifts)

    def getLoewdinCharges(self) -> list:
        """Extract Loewdin atomic charges."""
        charges = []
        for i, line in enumerate(self.lines):
            if "LOEWDIN ATOMIC CHARGES" in line:
                startIdx = i + 2
                currentCharges = []
                # Read charges until blank line
                while self.lines[startIdx].strip():
                    parts = self.lines[startIdx].split()
                    for i, part in enumerate(parts):
                        if part == ":":
                            parts = parts[:i] + parts[i + 1 :]
                    currentCharges.append({"atomNum": int(parts[0]), "atom": parts[1], "charge": float(parts[2])})
                    startIdx += 1
                charges.append(pd.DataFrame(currentCharges))
        return charges

    def extractConformers(self):
        """Extract conformer molecular structures."""
        # Get the Number of Atoms we should Expect
        if self.isFileReference():
            atomNum = XYZFile(self.molecule).atomCount
        else:
            atomNum = self.molecule.atomCount

        # Open the File
        ensembleXYZFile = open(os.path.join(self.orcaCachePath, f"{self.name}.finalensemble.xyz"))

        # Get all the Lines from the File
        allLines = ensembleXYZFile.readlines()

        # Get the Expected Length of a XYZ File
        XYZLength = atomNum + 2

        # Calculate the Number of
        moleculeCount = int((len(allLines)) / (XYZLength))

        for i in range(moleculeCount):
            # Get the Lines for a Single XYZ File
            molLines = allLines[i * XYZLength : (i + 1) * XYZLength :]

            # Make the Name
            moleculeName = f"{self.name}_Conf_{i}"

            # Load as a XYZ File
            xyz = XYZFile(molecule=molLines, name=moleculeName)

            # Convert to a Molecule
            molecule = Molecule(moleculeName, xyz)

            # Add to the Conformer List
            self.conformers.append(molecule)

    def gaussianBlur(self, data: list[float], sigma: float):
        """Applies a Gaussian Blur to the Inputted Data
        
        Parameters :
            data (list[float]) - List of data to apply a Gaussian Blur to
            sigma (float) - Standard Deviation or Spread of the Gaussian used to blur the data
            
        Returns :
            list[float] - List of the Blurred Data
        """
        
        size = int(len(data))
        halfSize = size // 2
        
        # Create a normalized Gaussian Kernel for Convolution
        kernel = np.exp(-np.linspace(-halfSize, halfSize, size)**2 / (2 * sigma**2))
        kernel = kernel / kernel.sum()
        
        paddedData = np.pad(data, len(kernel) // 2, mode="reflect")
        
        return np.convolve(paddedData, kernel, mode="valid")[:len(data)]
        
    def getProcessedIRSpectra(self, sigma:float = 5):
        """Processes the IR Spectra by padding the raw Wavenumbers and Intensities and applying a Gaussian Blur and Inverting the values
        
        Parameters :
            sigma (float) - The Standard Deviation or spread of the Gaussian Blur applied to the data
            
        Returns :
            pandas.DataFrame - A Padded DataFrame with the IR Spectra Inverted and Blurred with a Gaussian
        """
        if (self.IRFrequencies is None):
            raise RuntimeError("IR Frequencies have not been Calculated, cannot process data.")
        
        IRSpectra = self.IRFrequencies
        
        for i in range(0, 4300, 1):
            IRSpectra.loc[len(IRSpectra)] = [0, i, 0]
        
        # Group Common Wavenumbers and Sort the DataFrame
        IRSpectra.groupby("Wavenumber", as_index=False).agg({"IRIntensity": "sum"})
        IRSpectra = IRSpectra.sort_values(by="Wavenumber", ascending=False)
        
        # Apply Gaussian Blur
        IRSpectra["IRIntensity"] = self.gaussianBlur(IRSpectra["IRIntensity"].to_list(), sigma)
        
        # Normalize and Inverse the Intensity
        IRSpectra["IRIntensity"] = 1 - (
            IRSpectra["IRIntensity"].values / max(IRSpectra["IRIntensity"].values)
        )
        
        return IRSpectra
        
    def plotIRSpectra(self, sigma :float = 5):
        """Quickly Plots and Displays the Processed IR Spectra Graph
        
        Parameters :
            sigma (float) - The Standard Deviation or spread of the Gaussian Blur applied to the data
        """
        IRSpectra = self.getProcessedIRSpectra(sigma)
        
        # Plots the Spectra
        plt.figure()
        plt.plot(IRSpectra["Wavenumber"], IRSpectra["IRIntensity"])
        plt.xlabel("Wavenumber (1/cm)")
        plt.ylabel("IR Intensity")
        plt.gca().invert_xaxis()
        plt.show()
        
    def getNumberOfAtoms(self) -> int:
        """Extracts the number of Atoms Present in the Molecule"""
        
        for line in self.lines:
            if "Number of atoms" in line:
                return int(line.split()[-1])
        
        return 0
    
    def getNormalModes(self) -> pd.DataFrame:
        """Extracts the Normal Modes matrix from the output file."""
        startIdx = -1
        
        # Find where the NORMAL MODES section begins
        for i, line in enumerate(self.lines):
            if "NORMAL MODES" in line and "------------" in self.lines[i+1]:
                startIdx = i + 6 # Skip the headers and text
                break
                
        if startIdx == -1:
            return None
            
        numDof = self.atomNum * 3
        modesMatrix = np.zeros((numDof, numDof))
        
        # Parse the data blocks
        i = startIdx
        while i < len(self.lines):
            line = self.lines[i].strip()
            
            # Stop if we hit the next major section
            if "IR SPECTRUM" in line or line.startswith("------"):
                break
                
            # Skip empty lines
            if not line:
                i += 1
                continue
                
            parts = line.split()
            
            # Check if this is a column header line (all integers, no decimals)
            if all("." not in p for p in parts) and parts[0].isdigit():
                modeIndices = [int(p) for p in parts]
                
                # Read the data rows for these specific columns
                for j in range(numDof):
                    i += 1
                    dataParts = self.lines[i].split()
                    coordIdx = int(dataParts[0])
                    values = [float(x) for x in dataParts[1:]]
                    
                    # Store values in our 2D array
                    for colIdx, val in zip(modeIndices, values):
                        modesMatrix[coordIdx, colIdx] = val
            i += 1
            
        # Convert to a Pandas DataFrame
        columns = [f"Mode_{j}" for j in range(numDof)]
        return pd.DataFrame(modesMatrix, columns=columns)

    def getImaginaryModeDisplacements(self) -> np.ndarray:
        """Determines the XYZ displacement vectors to remove the imaginary frequency."""
        imaginaryModeIdx = -1
        
        # Find the index of the imaginary frequency
        for line in self.lines:
            if "***imaginary mode***" in line:
                parts = line.split(":")
                imaginaryModeIdx = int(parts[0].strip())
                break
                
        if imaginaryModeIdx == -1:
            print("No imaginary mode found in this file.")
            return None
            
        # Grab the full normal modes DataFrame
        normalModesDf = self.normalModes
        if normalModesDf is None:
            return None
            
        # Extract the specific column for our imaginary mode
        modeColName = f"Mode_{imaginaryModeIdx}"
        modeVector1D = normalModesDf[modeColName].values
        
        # Reshape the 1D array into an N x 3 grid
        displacementVectors = modeVector1D.reshape((self.atomNum, 3))
        
        return displacementVectors
    
    def getTotalEnthalpy(self) -> float:
        """Extracts the Total Enthalpy in Hartrees
        
        Returns:
            (float) - Total Enthalpy of the Molecule in Hartrees
        """
        for i, line in enumerate(self.lines):
            if ("ENTHALPY" in line and "--------" in self.lines[i+1]):
                index = i + 8
                value = self.lines[index].split("...")[1].strip() 
                value = value.removesuffix("Eh")
                value = float(value)
                return value
            
    def getTotalThermalEnergy(self) -> float:
        """Extracts the Total Thermal Energy in Hartrees
        
        Returns:
            (float) - Total Thermal Energy of the Molecule in Hartrees
        """
        for i, line in enumerate(self.lines):
            if ("ENTHALPY" in line and "--------" in self.lines[i+1]):
                index = i + 5
                value = self.lines[index].split("...")[1].strip() 
                value = value.removesuffix("Eh")
                value = float(value)
                return value
            
    def getThermalEnthalpyCorrection(self) -> float:
        """Extracts the Thermal Enthalpy Correction in Hartrees
        
        Returns:
            (float) - Thermal Enthalpy Correction of the Molecule in Hartrees
        """
        for i, line in enumerate(self.lines):
            if ("ENTHALPY" in line and "--------" in self.lines[i+1]):
                index = i + 6
                value = self.lines[index].split("...")[1].strip()
                value = value.split("Eh")[0].strip()
                value = float(value)
                return value
                
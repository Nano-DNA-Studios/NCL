import re
import os
import pandas as pd


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
        self.SCFEnergies = self.getSCFEnergies()
        self.finalTimings = self.getFinalTimings()
        self.mayerPopulation = self.getMayerPopulation()
        self.loedwin = self.getLoewdinCharges()
        self.dipole = self.getDipoleVector()
        self.absolutedipole = self.getDipoleMagnitude()
        self.energy = self.getFinalEnergy()

        # Extract calculation-specific data based on type
        self.vibrationalFrequencies = self.getVibrationalFrequencies() if "FREQ" in self.calculationTypes else None
        self.IRFrequencies = self.getIRFrequencies() if "FREQ" in self.calculationTypes else None
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
                                "mode": int(parts[0].strip(":")),
                                "frequency": float(parts[1]),
                            }
                        )
                    startIdx += 1

        # Return empty DataFrame if no frequencies found
        if len(freqs) == 0:
            return pd.DataFrame(columns=["mode", "frequency"])
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
                                "mode": int(parts[0].strip(":")),
                                "frequency": float(parts[1]),
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

import re
import os
from .Molecule import Molecule
from abc import ABC, abstractmethod


class InputFile(ABC):

    def __init__(self, name: str, extension: str, molecule: Molecule):

        if not isinstance(name, str):
            raise TypeError("The name of the Input File must be a string")

        if not isinstance(extension, str):
            raise TypeError("The extension of the Input File must be a string")
        
        if (not isinstance(molecule, Molecule)):
            raise TypeError("The Molecule passed in is not of Type Molecule!")

        if len(name.strip()) == 0:
            raise ValueError("The name cannot be empty")

        if len(extension.strip()) == 0:
            raise ValueError("The extension cannot be empty")

        if not extension.startswith("."):
            raise ValueError("The extension must start with a '.'")
        
        self.name = name
        self.extension = extension
        self.molecule = molecule

    @abstractmethod
    def build(self) -> str:
        """Builds and returns the input file content as a string"""
        pass

    def save(self, filePath : str):
        """Saves the build Input file to the location specified by filePath"""
        fullFilePath = os.path.join(filePath, self.name + self.extension)
        with open(fullFilePath, "w") as f:
            f.write(self.build())

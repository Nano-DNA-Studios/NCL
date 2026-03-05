import unittest
import os
from ncl import InputFile, Molecule

# Created a dummy class to test the abstract InputFile class
class DummyInputFile(InputFile):
    def build(self) -> str:
        return "dummy content"

class InputFileTest(unittest.TestCase):

    def setUp(self):
        self.name = "Propane"
        self.extension1 = ".inp"
        self.extension2 = ".lmp"
        self.filePath = "tests/Resources/Propane.xyz"
        self.molecule = Molecule(self.name, self.filePath)

    def test_constructor(self):
        """Tests the Constructor for the InputFile Class"""
        inputFile = DummyInputFile(self.name, self.extension1, self.molecule)

        self.assertEqual(self.name, inputFile.name)
        self.assertEqual(self.extension1, inputFile.extension)
        self.assertEqual(self.molecule, inputFile.molecule)

    def test_constructor_error(self):
        """Tests the Constructor Error throwing for the Input File Class"""
        with self.assertRaises(TypeError):
            DummyInputFile(1, self.extension1, self.molecule)

        with self.assertRaises(TypeError):
            DummyInputFile(self.name, 1, self.molecule)
            
        with self.assertRaises(TypeError):
            DummyInputFile(self.name, self.extension1, "Not a molecule")

        with self.assertRaises(ValueError):
            DummyInputFile("", self.extension1, self.molecule)

        with self.assertRaises(ValueError):
            DummyInputFile(self.name, "", self.molecule)

        with self.assertRaises(ValueError):
            DummyInputFile(" ", self.extension1, self.molecule)

        with self.assertRaises(ValueError):
            DummyInputFile(self.name, "inp", self.molecule)
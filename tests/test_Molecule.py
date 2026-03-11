import unittest
import re
from ncl import Molecule

class MolecueTest(unittest.TestCase):

    def setUp(self):

        self.name = "Propane"
        self.filePath = "tests/Resources/Propane.xyz"

        self.columns = ["Atom", "X", "Y", "Z"]
        self.atomNum = 11

    def test_contructor(self):

        molecule = Molecule(self.name, self.filePath)

        self.assertIsNotNone(molecule)
        self.assertEqual(self.name, molecule.name)
        self.assertEqual(self.filePath, molecule.filePath)

        self.assertIsNotNone(molecule.positions)
        self.assertEqual(4, len(molecule.positions.columns))
        self.assertEqual("Atom", molecule.positions.columns[0])
        self.assertEqual("X", molecule.positions.columns[1])
        self.assertEqual("Y", molecule.positions.columns[2])
        self.assertEqual("Z", molecule.positions.columns[3])
        self.assertEqual(self.atomNum, len(molecule.positions["Atom"]))

    def test_constructor_error(self):

        with self.assertRaises(TypeError):
            Molecule(1, self.filePath)

        with self.assertRaises(TypeError):
            Molecule(self.name, 1)

        with self.assertRaises(ValueError):
            Molecule("", self.filePath)

        with self.assertRaises(ValueError):
            Molecule(self.name, "")

        with self.assertRaises(ValueError):
            Molecule(" ", self.filePath)

        with self.assertRaises(ValueError):
            Molecule(self.name, " ")

        with self.assertRaises(FileNotFoundError):
            Molecule(self.name, "nonExistantFile.xyz")

    def test_getContent(self):

        molecule = Molecule(self.name, self.filePath)
        positions = molecule.getContent()
        lines = positions.split("\n")

        self.assertEqual(self.atomNum, len(lines))

        pattern = re.compile(
            r"^[A-Z][a-z]?\s+[-+]?\d*\.\d+\s+[-+]?\d*\.\d+\s+[-+]?\d*\.\d+$"
        )

        for line in lines:
            self.assertRegex(line.strip(), pattern)

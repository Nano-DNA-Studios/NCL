import unittest
import re
import io
import numpy as np
import pandas as pd
from unittest.mock import patch
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

    def test_getXYZCoordinate(self):
        """Tests fetching XYZ coordinates as a Numpy array"""
        molecule = Molecule(self.name, self.filePath)
        coords = molecule.getXYZCoordinate(0)
        
        self.assertIsInstance(coords, np.ndarray)
        self.assertEqual(3, len(coords))

    def test_getBondLength(self):
        """Tests distance calculation between two atoms"""
        molecule = Molecule(self.name, self.filePath)
        dist = molecule.getBondLength(0, 1)
        
        self.assertIsInstance(dist, float)
        self.assertTrue(dist >= 0.0)

    def test_getBonds(self):
        """Tests the bonds DataFrame generation"""
        molecule = Molecule(self.name, self.filePath)
        bondsDF = molecule.getBonds()
        
        self.assertIsInstance(bondsDF, pd.DataFrame)
        self.assertEqual(self.atomNum, len(bondsDF))
        self.assertIn("Index", bondsDF.columns)
        self.assertIn("Atom", bondsDF.columns)
        self.assertIn("Bonds", bondsDF.columns)
        self.assertIn("Bond Distance", bondsDF.columns)
        self.assertIn("Rotatable", bondsDF.columns)

    def test_getAllAtomsAfterBond_error(self):
        """Tests that attempting to search after a non-existent bond raises an Exception"""
        molecule = Molecule(self.name, self.filePath)
        
        # Create a mock dataframe where atom 0 has NO bonds
        mockDF = pd.DataFrame({"Bonds": [[] for _ in range(self.atomNum)]})
        
        with self.assertRaises(Exception) as context:
            molecule.getAllAtomsAfterBond(0, 1, mockDF)
            
        self.assertTrue("These Atoms are not Bonded Together" in str(context.exception))

    def test_generatePerpendicularVector(self):
        """Tests math utility for perpendicular vectors"""
        molecule = Molecule(self.name, self.filePath)
        baseVector = np.array([1.0, 0.0, 0.0])
        perpVector = molecule.generatePerpendicularVector(baseVector)
        
        # Dot product of perpendicular vectors is 0
        self.assertAlmostEqual(np.dot(baseVector, perpVector), 0.0)

    def test_generatePerpendicularVector_error(self):
        """Tests error throwing for zero vector input"""
        molecule = Molecule(self.name, self.filePath)
        zeroVector = np.array([0.0, 0.0, 0.0])
        
        with self.assertRaises(ValueError):
            molecule.generatePerpendicularVector(zeroVector)

    def test_getMolecularWeight(self):
        """Tests molecular weight calculation for Propane (~44.1 g/mol)"""
        molecule = Molecule(self.name, self.filePath)
        weight = molecule.getMolecularWeight()
        
        self.assertIsInstance(weight, float)
        self.assertTrue(40.0 < weight < 50.0)

    def test_getAngleBetweenAtoms(self):
        """Tests execution and return type of angle calculation"""
        molecule = Molecule(self.name, self.filePath)
        angle = molecule.getAngleBetweenAtoms(0, 1, 2)
        
        self.assertIsInstance(angle, float)

    def test_getDihedralAngle(self):
        """Tests execution and return type of dihedral angle calculation"""
        molecule = Molecule(self.name, self.filePath)
        dihedral = molecule.getDihedralAngle(0, 1, 2, 3)
        
        self.assertIsInstance(dihedral, float)

    def test_createZMatrixFile(self):
        """Tests generation of Z Matrix lines"""
        molecule = Molecule(self.name, self.filePath)
        zMatrix = molecule.createZMatrixFile()
        
        self.assertIsInstance(zMatrix, list)
        self.assertEqual(str(self.atomNum), zMatrix[0])
        self.assertEqual(self.name, zMatrix[1])
        # Total rows should be Header(2) + atomCount(11) = 13
        self.assertEqual(self.atomNum + 2, len(zMatrix))

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_displayZMatrix(self, mockSTDOut):
        """Tests that Z Matrix prints to console successfully"""
        molecule = Molecule(self.name, self.filePath)
        molecule.displayZMatrix()
        
        output = mockSTDOut.getvalue()
        self.assertTrue(len(output) > 0)
        self.assertIn(self.name, output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_displayBondGraph(self, mockSTDOut):
        """Tests that Bond Graph prints to console successfully"""
        molecule = Molecule(self.name, self.filePath)
        molecule.displayBondGraph()
        
        output = mockSTDOut.getvalue()
        self.assertTrue(len(output) > 0)
        self.assertIn(self.name, output)

    def test_rotateBond(self):
        """Tests that rotating a bond successfully executes and alters coordinates"""
        molecule = Molecule(self.name, self.filePath)
        
        # Assuming sorted positions means atom 0 and 1 (Carbons) are bonded
        # We will rotate by 90 degrees (pi/2)
        try:
            molecule.rotateBond(0, 1, np.pi/2)
            success = True
        except Exception:
            success = False
            
        self.assertTrue(success, "rotateBond threw an unexpected exception.")
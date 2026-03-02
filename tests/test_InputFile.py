import unittest
from ncl import InputFile

# Implement DocStrings tomorrow
class InputFileTest(unittest.TestCase):

    def setUp(self):

        self.name = "Propane"
        self.extension1 = ".inp"
        self.extension2 = ".lmp"

        self.template = "!&{calculation} &{basis} &{functional}"
        self.expectedOutput = "!HF DEF2-SVP B3LYP"
        self.args = {"calculation": "HF", "basis": "DEF2-SVP", "functional": "B3LYP"}

        self.inputFile = InputFile(self.name, self.extension1)

        return super().setUp()

    def test_constructor(self):
        """Tests the Constructor for the InputFile Class

        Ensures the Class is properly initialized and the Variables are their expected Default Values
        """
        inputFile = InputFile(self.name, self.extension1)

        self.assertEqual(self.name, inputFile.name)
        self.assertEqual(self.extension1, inputFile.extension)
        self.assertEqual("", inputFile._header)
        self.assertEqual("", inputFile._footer)
        self.assertListEqual([], inputFile._structures)

        inputFile = InputFile(self.name, self.extension2)

        self.assertEqual(self.name, inputFile.name)
        self.assertEqual(self.extension2, inputFile.extension)
        self.assertEqual("", inputFile._header)
        self.assertEqual("", inputFile._footer)
        self.assertListEqual([], inputFile._structures)

    def test_constructor_error(self):
        """Tests the Constructor Error throwing for the Input File Class

        Ensures the proper Errors are thrown when a Improper Values are provided to the Constructor
        """
        with self.assertRaises(TypeError):
            InputFile(1, self.extension1)

        with self.assertRaises(TypeError):
            InputFile(self.name, 1)

        with self.assertRaises(ValueError):
            InputFile("", self.extension1)

        with self.assertRaises(ValueError):
            InputFile(self.name, "")

        with self.assertRaises(ValueError):
            InputFile(" ", self.extension1)

        with self.assertRaises(ValueError):
            InputFile(self.name, " ")

        with self.assertRaises(ValueError):
            InputFile(self.name, "inp")

    def test_compile(self):
        expectedOutput = self.expectedOutput
        inputFile = self.inputFile
        template = self.template

        output = inputFile.compile(template, calculation="HF", basis="DEF2-SVP", functional="B3LYP")

        self.assertIsNotNone(output)
        self.assertEqual(expectedOutput, output)

        output = inputFile.compile(expectedOutput)

        self.assertIsNotNone(output)
        self.assertEqual(expectedOutput, output)

    def test_compile_error(self):
        """Tests the compile functions Error throwing

        Ensures the proper Errors are thrown when Improper Values are provided to the compile function

        Input :
            template : 1
        Output :
            TypeError

        Input :
            args : ""
        Output :
            TypeError

        Input :
            template : ""
        Output :
            ValueError

        Input :
            template : " "
        Output :
            ValueError

        Input :
            template : "!&{calculation} &{basis} &{functional}"
            args : None
        Output :
            ValueError
        """
        inputFile = self.inputFile

        with self.assertRaises(TypeError):
            inputFile.compile(1)

        with self.assertRaises(TypeError):
            inputFile.compile(self.template, "")

        with self.assertRaises(ValueError):
            inputFile.compile("")

        with self.assertRaises(ValueError):
            inputFile.compile(" ")

        with self.assertRaises(ValueError):
            inputFile.compile(self.template)

    def test_setHeader(self):

        expectedOutput = self.expectedOutput
        inputFile = self.inputFile
        template = self.template

        inputFile.setHeader(template, calculation="HF", basis="DEF2-SVP", functional="B3LYP")

        self.assertEqual(expectedOutput, inputFile._header)

        inputFile.setHeader(expectedOutput)

        self.assertEqual(expectedOutput, inputFile._header)

    def test_setHeader_error(self):
        inputFile = self.inputFile

        with self.assertRaises(TypeError):
            inputFile.setHeader(1)

        with self.assertRaises(TypeError):
            inputFile.setHeader(self.template, "")

        with self.assertRaises(ValueError):
            inputFile.setHeader("")

        with self.assertRaises(ValueError):
            inputFile.setHeader(" ")

        with self.assertRaises(ValueError):
            inputFile.setHeader(self.template)

    def test_setFooter(self):

        expectedOutput = self.expectedOutput
        inputFile = self.inputFile
        template = self.template

        inputFile.setFooter(
            template, calculation="HF", basis="DEF2-SVP", functional="B3LYP"
        )

        self.assertNotEqual("", inputFile._footer)
        self.assertEqual(expectedOutput, inputFile._footer)

        inputFile.setFooter(expectedOutput)

        self.assertNotEqual("", inputFile._footer)
        self.assertEqual(expectedOutput, inputFile._footer)

    def test_setFooter_error(self):
        inputFile = self.inputFile

        with self.assertRaises(TypeError):
            inputFile.setFooter(1)

        with self.assertRaises(TypeError):
            inputFile.setFooter(self.template, "")

        with self.assertRaises(ValueError):
            inputFile.setFooter("")

        with self.assertRaises(ValueError):
            inputFile.setFooter(" ")

        with self.assertRaises(ValueError):
            inputFile.setFooter(self.template)

    def test_build(self):

        expectedOutput = self.expectedOutput
        inputFile = self.inputFile

        self.assertIsNotNone(inputFile.build())
        self.assertEqual("", inputFile.build())

        inputFile.setHeader(expectedOutput)
        
        self.assertIsNotNone(inputFile.build())
        self.assertEqual(expectedOutput, inputFile.build().replace("\n", ""))
        
        inputFile.setFooter(expectedOutput)
        
        self.assertIsNotNone(inputFile.build())
        self.assertEqual(expectedOutput*2, inputFile.build().replace("\n", ""))
        
        inputFile.addStructure(expectedOutput)
        
        self.assertIsNotNone(inputFile.build())
        self.assertEqual(expectedOutput*3, inputFile.build().replace("\n", ""))
        
        inputFile.addStructure(expectedOutput)
        
        self.assertIsNotNone(inputFile.build())
        self.assertEqual(expectedOutput*4, inputFile.build().replace("\n", ""))
        
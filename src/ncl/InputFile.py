import re
import os
from abc import ABC


class InputFile(ABC):

    def __init__(self, name: str, extension: str):

        if not isinstance(name, str):
            raise TypeError("The name of the Input File must be a string")

        if not isinstance(extension, str):
            raise TypeError("The extension of the Input File must be a string")

        if len(name.strip()) == 0:
            raise ValueError("The name cannot be empty")

        if len(extension.strip()) == 0:
            raise ValueError("The extension cannot be empty")

        if not extension.startswith("."):
            raise ValueError("The extension must start with a '.'")

        self.name = name
        self.extension = extension
        self._header: str = ""
        self._footer: str = ""
        self._structures: list[str] = []

    def compile(self, template: str, **args: dict[str, str]):

        if not isinstance(template, str):
            raise TypeError("The template must be a string")

        if not isinstance(args, dict):
            raise TypeError("The arguments must be of type string")

        if len(template.strip()) == 0:
            raise ValueError("The template cannot be empty")

        pattern = r"&\{(\w+)\}"
        keys = re.findall(pattern, template)

        if len(keys) == 0:
            return template

        for key in keys:
            if key not in args:
                raise ValueError(f"Key {key} is not found in Arguments")

            template = template.replace(f"&{{{key}}}", args[key])

        return template

    def setHeader(self, header: str = None, **args: dict[str, str]):
        self._header = self.compile(header, **args)

    def setFooter(self, footer: str = None, **args: dict[str, str]):
        self._footer = self.compile(footer, **args)

    def addStructure(self, structure: str = None, **args: dict[str, str]):
        self._structures.append(self.compile(structure, **args))

    def build(self) -> str:

        if self._header != "":
            fileContent = self._header + "\n"
        else:
            fileContent = ""

        for line in self._structures:
            fileContent += line + "\n"

        fileContent += self._footer

        return fileContent

    def save(self, filePath : str):
    
        with open(os.path.join(filePath, self.name + self.extension), "w") as f:
            f.write(self.build())

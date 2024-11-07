import os
from dataclasses import dataclass, field
import random
import re
from typing import List


@dataclass
class MethodModel:
    name: str


@dataclass
class ClassModel:
    name: str
    methods: List[MethodModel] = field(default_factory=list)
    directory: str = ""
    filename: str = ""
    parents: List[str] = field(default_factory=list)


class PythonStaticAnalyzer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.model = []

    def analyze(self):
        for root, _, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith(".py"):
                    self._analyze_file(os.path.join(root, file), root, file)

    def _remove_comments_from_code(self, code):
        # Удаляем строки комментариев, начинающихся с #, игнорируя # внутри строк
        code = re.sub(r'(?<!\\)#.*', '', code)
        # Удаляем многострочные комментарии, заключенные в тройные кавычки """ или '''
        code = re.sub(r'\'\'\'(.*?)\'\'\'|"""(.*?)"""', '', code, flags=re.DOTALL)
        return code

    def _analyze_file(self, file_path, directory, filename):
        current_class = None
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            content = self._remove_comments_from_code(content).splitlines()
            for line in content:
                stripped_line = line.strip()

                if stripped_line.startswith("class "):
                    class_name, parents = self._extract_class_name_and_parents(
                        stripped_line
                    )
                    current_class = ClassModel(
                        name=class_name,
                        directory=directory,
                        filename=filename,
                        parents=parents,
                    )
                    self.model.append(current_class)

                elif stripped_line.startswith("def ") and current_class:
                    method_name = self._extract_method_name(stripped_line)
                    current_class.methods.append(MethodModel(name=method_name))

    def _extract_class_name_and_parents(self, line):
        class_declaration = line.split("class ")[1].split(":")[0].strip()
        parts = class_declaration.split("(")
        class_name = parts[0].strip()
        class_name = class_name.replace(".", "_")
        parents = (
            [p.strip() for p in parts[1][:-1].split(",")] if len(parts) > 1 else []
        )
        parents = [p.replace(".", "_") for p in parents]
        return class_name, parents

    def _extract_method_name(self, line):
        method_declaration:str = line.split("def ")[1].split("(")[0].strip()
        method_declaration = method_declaration.replace('.' , '_')
        return method_declaration

    def get_model(self):
        return self.model

    def generate_test_data(self):
        # Names for our 5 test classes
        class_names = ["ClassA", "ClassB", "ClassC", "ClassD", "ClassE"]
        methods_per_class = 3

        # Generate 5 classes with 3 methods each
        for class_name in class_names:
            methods = [
                MethodModel(name=f"method_{i+1}") for i in range(methods_per_class)
            ]
            self.model.append(ClassModel(name=class_name, methods=methods))

        # Create random inheritance relationships between classes
        num_relationships = 5
        relationships = set()

        while len(relationships) < num_relationships:
            parent = random.choice(class_names)
            child = random.choice(class_names)
            if parent != child:  # Ensure no class inherits from itself
                relationships.add((child, parent))

        # Apply relationships to the class models
        for child, parent in relationships:
            for class_model in self.model:
                if class_model.name == child:
                    class_model.parents.append(parent)

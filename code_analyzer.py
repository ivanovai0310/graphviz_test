import json
import os
from dataclasses import asdict, dataclass, field
import re
from typing import List, Dict


@dataclass
class MethodModel:
    name: str
    calls: List[str] = field(default_factory=list)


@dataclass
class ClassModel:
    name: str
    methods: List[MethodModel] = field(default_factory=list)
    parents: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)
    directory: str = ""
    filename: str = ""


class PythonStaticAnalyzer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.model: Dict[str, ClassModel] = {}
        self.all_classes = set()

    def analyze(self):
        for root, _, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                        code = self._remove_comments_from_code(code)
                        self._extract_classes(code, root, file)
                        self._extract_methods_and_calls(code)

        self._add_missing_parents()

    def _remove_comments_from_code(self, code):
        code = re.sub(r"(?<!\\)#.*", "", code)
        code = re.sub(r'\'\'\'(.*?)\'\'\'|"""(.*?)"""', "", code, flags=re.DOTALL)
        return code

    def _sanitize_name(self, name):
        return re.sub(r"\[.*?\]", "", name)

    def _extract_classes(self, code, directory, filename):
        class_pattern = r"class\s+(\w+)(?:\((.*?)\))?:"
        for match in re.finditer(class_pattern, code):
            class_name = self._sanitize_name(match.group(1))
            parents = (
                [
                    self._sanitize_name(parent.strip().replace(".", "_"))
                    for parent in match.group(2).split(",")
                ]
                if match.group(2)
                else []
            )
            self.model[class_name] = ClassModel(
                name=class_name,
                parents=parents,
                directory=directory,
                filename=filename,
            )
            self.all_classes.add(class_name)

    def _extract_methods_and_calls(self, code):
        class_body_pattern = r"class\s+(\w+)(?:\(.*?\))?:\s*(.*?)\n(?=class|\Z)"
        method_pattern = r"def\s+(\w+)\s*\("
        call_pattern = r"\b(\w+)\("

        for class_match in re.finditer(class_body_pattern, code, re.DOTALL):
            class_name = self._sanitize_name(class_match.group(1))
            class_body = class_match.group(2)

            current_class = self.model.get(class_name)
            if not current_class:
                continue

            method_dict = {}
            unique_calls = set()

            for method_match in re.finditer(method_pattern, class_body):
                method_name = method_match.group(1)
                method_model = MethodModel(name=method_name)
                current_class.methods.append(method_model)
                method_dict[method_name] = method_model

            for method_model in current_class.methods:
                method_start = class_body.find(f"def {method_model.name}(")
                method_body = class_body[method_start:]

                for call_match in re.finditer(call_pattern, method_body):
                    called_name = self._sanitize_name(call_match.group(1))
                    if called_name in method_dict:
                        method_model.calls.append(called_name)
                    elif called_name not in unique_calls and called_name != class_name:
                        method_model.calls.append(called_name)
                        unique_calls.add(called_name)

    def _add_missing_parents(self):
        val = self.model.copy() 
        for class_model in val.values():
            for parent in class_model.parents:
                if parent not in self.model:
                    # Добавляем родительский класс в модель
                    self.model[parent] = ClassModel(
                        name=parent,
                        directory="python_and_other_modules",
                        filename="path unknown",
                    )
                    self.all_classes.add(parent)

    def get_model(self):
        return self.model

    def save_model_to_json(self, filepath):
        model_dict = {
            class_name: asdict(class_model)
            for class_name, class_model in self.model.items()
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(model_dict, f, indent=4, ensure_ascii=False)

    def filter_model_by_tracer(self, tracer):
        all_tracer_classes = {el.class_name for el in tracer}
        model_val = self.model.copy()
        filtred_model = {}
        for _name, _class in model_val.items():
            if _name in all_tracer_classes:
                filtred_model[_name] = _class
        self.model = filtred_model
        #add filtred connections
        

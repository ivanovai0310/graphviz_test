import os
from dataclasses import dataclass, field
import re
from typing import List, Dict


@dataclass
class MethodModel:
    name: str
    calls: List[str] = field(
        default_factory=list
    )  # Вызовы других методов внутри метода или других классов


@dataclass
class ClassModel:
    name: str
    methods: List[MethodModel] = field(default_factory=list)
    parents: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)  # Вызовы других классов из методов
    directory: str = ""  # Каталог, где находится файл
    filename: str = ""  # Имя файла


class PythonStaticAnalyzer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.model: Dict[str, ClassModel] = {}

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

    def _remove_comments_from_code(self, code):
        # Удаление строковых и многострочных комментариев
        code = re.sub(r"(?<!\\)#.*", "", code)
        code = re.sub(r'\'\'\'(.*?)\'\'\'|"""(.*?)"""', "", code, flags=re.DOTALL)
        return code

    def _sanitize_name(self, name):
        # Удаляет любые параметры в квадратных скобках
        return re.sub(r"\[.*?\]", "", name)

    def _extract_classes(self, code, directory, filename):
        # Находит все классы с опциональным наследованием
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
            # Добавляем класс в модель с информацией о пути к файлу и имени файла
            self.model[class_name] = ClassModel(
                name=class_name,
                parents=parents,
                directory=directory,
                filename=filename,
            )

    def _extract_methods_and_calls(self, code):
        # Находим все методы и связываем их с классами
        class_body_pattern = r"class\s+(\w+)(?:\(.*?\))?:\s*(.*?)\n(?=class|\Z)"
        method_pattern = r"def\s+(\w+)\s*\("
        call_pattern = r"\b(\w+)\("

        for class_match in re.finditer(class_body_pattern, code, re.DOTALL):
            class_name = self._sanitize_name(class_match.group(1))
            class_body = class_match.group(2)

            current_class = self.model.get(class_name)
            if not current_class:
                continue

            # Словарь для отслеживания методов текущего класса
            method_dict = {}
            unique_calls = set()

            # Извлекаем методы и сохраняем их в словарь
            for method_match in re.finditer(method_pattern, class_body):
                method_name = method_match.group(1)
                method_model = MethodModel(name=method_name)
                current_class.methods.append(method_model)
                method_dict[method_name] = (
                    method_model  # Сохраняем метод для ссылок внутри класса
                )

            # Извлекаем вызовы и добавляем их как вызовы внутри класса, если метод найден
            for method_model in current_class.methods:
                method_start = class_body.find(f"def {method_model.name}(")
                method_body = class_body[method_start:]

                for call_match in re.finditer(call_pattern, method_body):
                    called_name = self._sanitize_name(call_match.group(1))

                    # Проверка, является ли вызов методом текущего класса
                    if called_name in method_dict:
                        # Если вызывается метод текущего класса
                        method_model.calls.append(called_name)
                    elif called_name not in unique_calls and called_name != class_name:
                        # Если вызывается внешний класс
                        method_model.calls.append(called_name)
                        unique_calls.add(called_name)

    def get_model(self):
        return self.model

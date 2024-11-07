import os
from dataclasses import dataclass, field
import re
from typing import List, Dict


@dataclass
class MethodModel:
    name: str
    calls: List[str] = field(
        default_factory=list
    )  # Вызовы других классов внутри метода


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
        # Объединяем все исходные тексты файлов и анализируем каждый файл
        for root, _, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                        code = self._remove_comments_from_code(code)
                        # Извлекаем классы и методы для каждого файла отдельно
                        self._extract_classes(code, root, file)
                        self._extract_methods_and_calls(code)

    def _remove_comments_from_code(self, code):
        # Удаляем строки комментариев и многострочные комментарии
        code = re.sub(r"(?<!\\)#.*", "", code)
        code = re.sub(r'\'\'\'(.*?)\'\'\'|"""(.*?)"""', "", code, flags=re.DOTALL)
        return code

    def _sanitize_name(self, name):
        # Удаляет любые параметры в квадратных скобках, например, [DeliveryProfile]
        return re.sub(r"\[.*?\]", "", name)

    def _extract_classes(self, code, directory, filename):
        # Находим все классы с опциональным наследованием
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

            # Извлекаем методы класса
            for method_match in re.finditer(method_pattern, class_body):
                method_name = method_match.group(1)
                method_model = MethodModel(name=method_name)

                # Извлекаем вызовы внутри метода
                method_start = method_match.end()
                method_body = class_body[method_start:]

                for call_match in re.finditer(call_pattern, method_body):
                    called_class = self._sanitize_name(call_match.group(1))

                    # Проверка, чтобы избежать самосвязей
                    if called_class != class_name:
                        method_model.calls.append(called_class)
                        if called_class in self.model:
                            current_class.calls.append(called_class)

                current_class.methods.append(method_model)

    def get_model(self):
        return self.model

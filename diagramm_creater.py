from typing import Dict
from code_analyzer import ClassModel, PythonStaticAnalyzer
import os


class GraphvizDiagramBuilder:
    def __init__(self, model: Dict[str, ClassModel]):
        self.model = model

    def _sanitize_node_name(self, name):
        # Экранируем имя узла для Graphviz
        return f'"{name}"'

    def build_diagram(self):
        # Начало диаграммы в формате Graphviz
        diagram = [
            "digraph UML_Class_diagram {",
            "\tgraph [",
            '\t\tlabel="UML Class diagram demo"',
            '\t\tlabelloc="t"',
            '\t\tfontname="Helvetica,Arial,sans-serif"',
            "\t];",
            "\tnode [",
            '\t\tfontname="Helvetica,Arial,sans-serif"',
            "\t\tshape=record",
            "\t\tstyle=filled",
            "\t\tfillcolor=gray95",
            "\t];",
            '\tedge [fontname="Helvetica,Arial,sans-serif"];',
        ]

        # Создание узлов для каждого класса с комментарием о пути к файлу
        for class_name, class_info in self.model.items():
            sanitized_class_name = self._sanitize_node_name(class_name)

            # Формируем строку с методами
            methods = '<br align="left"/>'.join(
                f"+ {method.name}()" for method in class_info.methods
            )
            methods_section = methods if methods else "No methods"
            label = f'<{{<b>{class_name}</b>|{methods_section}<br align="left"/>}}>'
            diagram.append(f"\t{sanitized_class_name} [label={label}];")

            # Добавляем комментарий с путём к файлу
            relative_path = os.path.join(
                os.path.basename(os.path.dirname(class_info.directory)),
                class_info.filename,
            )
            diagram.append(f"// {sanitized_class_name} located at {relative_path}")

        # Добавление связей для представления отношений наследования
        for class_name, class_info in self.model.items():
            sanitized_class_name = self._sanitize_node_name(class_name)
            for parent in class_info.parents:
                sanitized_parent = self._sanitize_node_name(parent)
                diagram.append(
                    f'\t{sanitized_class_name} -> {sanitized_parent} [dir="back" arrowtail="empty" style=""];'
                )

            # Добавление связей для вызовов других классов из методов
            for method in class_info.methods:
                for called_class in method.calls:
                    if called_class in self.model:
                        sanitized_called_class = self._sanitize_node_name(called_class)
                        # Добавляем точку в начале и стрелку на конце для вызовов от метода
                        diagram.append(
                            f"\t{sanitized_class_name} -> {sanitized_called_class} "
                            '[style="dashed" color="blue" arrowtail="dot" arrowhead="normal"];'
                        )

        # Завершение диаграммы
        diagram.append("}")
        return "\n".join(diagram)

    def save_diagram(self, output_file="UML_Class_diagram.gv"):
        diagram_text = self.build_diagram()
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(diagram_text)
        print(f"UML Class Diagram сохранена в {output_file}")


# Пример использования с тестовой моделью
if __name__ == "__main__":
    # Создание экземпляра PythonStaticAnalyzer и генерация тестовых данных
    analyzer = PythonStaticAnalyzer("")
    analyzer.analyze()  # Запуск анализа для создания модели
    model: Dict[str, ClassModel] = analyzer.get_model()

    # Создание и сохранение UML-диаграммы в формате .gv
    diagram_builder = GraphvizDiagramBuilder(model)
    diagram_builder.save_diagram("UML_Class_diagram.gv")

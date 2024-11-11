from enum import Enum
from typing import Dict
from graphviz import Digraph, Source
from code_analyzer import ClassModel, PythonStaticAnalyzer
import os


class Modes(str, Enum):
    TRACER = "tracer"
    CONNECTIONS = "connections"


class GraphvizDiagramBuilder:
    def __init__(self, model: Dict[str, ClassModel], mode:Modes,):
        self.model = model
        self.mode = mode

    def _sanitize_node_name(self, name):
        return f"_{name}" if name in "Node" else name

    def build_diagram(self):
        diagram = [
            "digraph UML_Class_diagram {",
            "\tgraph [",
            '\t\tlabel="UML Class diagram"',
            '\t\tlabelloc="t"',
            '\t\tfontname="Helvetica,Arial,sans-serif"',
            "\t\tranksep=2.0;",  # Увеличение вертикального расстояния между уровнями
            "\t\tnodesep=1.0;",  # Увеличение горизонтального расстояния между узлами
            "\t];",
            "\tnode [",
            '\t\tfontname="Helvetica,Arial,sans-serif"',
            "\t\tshape=none",  # Используем форму `none` для поддержки HTML-таблиц
            "\t];",
            '\tedge [fontname="Helvetica,Arial,sans-serif"];',
        ]

        # Группировка классов по директориям
        classes_by_directory = {}
        for class_name, class_info in self.model.items():
            directory = class_info.directory
            if directory not in classes_by_directory:
                classes_by_directory[directory] = []
            classes_by_directory[directory].append(class_info)

        # Создание подграфов для каждой директории
        for directory, classes in classes_by_directory.items():
            sanitized_directory_name = self._sanitize_node_name(
                directory.replace("/", "_").replace("-", "_")
            )
            directory_sanitize = (
                directory[directory.find("src") - 1 :]
                if directory.find("src") > 0
                else directory
            )
            diagram.append(f"subgraph cluster_{sanitized_directory_name} {{")
            # Используем полный путь к директории в качестве заголовка
            diagram.append(f'\tlabel="{directory_sanitize}";')
            diagram.append("\tstyle=filled;")
            diagram.append("\tcolor=lightgreen;")

            for class_info in classes:
                sanitized_class_name = self._sanitize_node_name(class_info.name)
                methods_rows = "".join(
                    f'<tr><td align="left" port="{method.name}">+ {method.name}()</td></tr>'
                    for method in class_info.methods
                )
                methods_section = (
                    methods_rows if methods_rows else "<tr><td>No methods</td></tr>"
                )
                label = f"""<<table border="2" cellborder="1" cellspacing="0">
                    <tr><td align="center" bgcolor="lightgray"><b>{class_info.name}</b></td></tr>
                    <tr><td align="center">{os.path.basename(class_info.filename)}</td></tr>
                    {methods_section}
                </table>>"""
                diagram.append(f'\t{sanitized_class_name} [label={label}, style=filled, color="#F0F0F0"];')

            diagram.append("}")

        # Добавление связей
        for class_name, class_info in self.model.items():
            sanitized_class_name = self._sanitize_node_name(class_name)
            for parent in class_info.parents:
                sanitized_parent = self._sanitize_node_name(parent)
                diagram.append(
                    f'\t{sanitized_class_name} -> {sanitized_parent} [dir="back" arrowtail="empty" style=""];'
                )

            # Добавляем связи от методов
            for method in class_info.methods:
                method_node_name = f"{sanitized_class_name}:{method.name}"
                for called_class in method.calls:
                    if called_class in self.model:
                        sanitized_called_class = self._sanitize_node_name(called_class)
                        diagram.append(
                            f"\t{method_node_name} -> {sanitized_called_class} "
                            '[color="blue" arrowtail="diamond" arrowhead="normal"];'
                        )

        diagram.append("}")
        return "\n".join(diagram)

    def save_diagram(self, output_file="UML_Class_diagram.gv"):
        diagram_text = self.build_diagram()
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(diagram_text)
        print(f"UML Class Diagram сохранена в {output_file}")

    def save_diagram_png(self, output_file="UML_Class_diagram"):
        diagram_text = self.build_diagram()
        diagram = Source(diagram_text)
        diagram.format = "png"
        diagram.render(filename=output_file, cleanup=True)

        print(f"UML Class Diagram сохранена в {output_file}")

    def save_diagram_svg(self, output_file="UML_Class_diagram"):
        diagram_text = self.build_diagram()
        diagram = Source(diagram_text)
        diagram.format = "svg"
        diagram.render(filename=output_file, cleanup=True)
        print(f"UML Class Diagram сохранена в {output_file}")

    def save_diagram_pdf(self, output_file="UML_Class_diagram"):
        diagram_text = self.build_diagram()
        diagram = Source(diagram_text)
        diagram.format = "pdf"
        diagram.render(filename=output_file, cleanup=True)
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

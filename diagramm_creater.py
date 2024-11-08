from typing import Dict

from graphviz import Source
from code_analyzer import ClassModel, PythonStaticAnalyzer
import os


class GraphvizDiagramBuilder:
    def __init__(self, model: Dict[str, ClassModel]):
        self.model = model

    def _sanitize_node_name(self, name):
        return f"_{name}" if name in "Node" else name

    def build_diagram(self):
        diagram = [
            "digraph UML_Class_diagram {",
            "\tgraph [",
            '\t\tlabel="UML Class diagram demo"',
            '\t\tlabelloc="t"',
            '\t\tfontname="Helvetica,Arial,sans-serif"',
            "\t];",
            "\tnode [",
            '\t\tfontname="Helvetica,Arial,sans-serif"',
            "\t\tshape=none",  # Используем форму `none` для поддержки HTML-таблиц
            "\t];",
            '\tedge [fontname="Helvetica,Arial,sans-serif"];',
        ]

        for class_name, class_info in self.model.items():
            sanitized_class_name = self._sanitize_node_name(class_name)
            relative_path = (
                os.path.basename(os.path.dirname(class_info.directory))
                + "/"
                + class_info.filename
            )

            # Создание HTML-таблицы для класса
            methods_rows = "".join(
                f'<tr><td align="left" port="{method.name}">+ {method.name}()</td></tr>'
                for method in class_info.methods
            )
            methods_section = (
                methods_rows if methods_rows else "<tr><td>No methods</td></tr>"
            )

            label = f"""<<table border="0" cellborder="1" cellspacing="0">
                <tr><td><b>{class_name}</b></td></tr>
                <tr><td>{relative_path}</td></tr>
                {methods_section}
            </table>>"""
            diagram.append(f"\t{sanitized_class_name} [label={label}];")

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
                            '[ color="blue" arrowtail="diamond" arrowhead="diamond"];'  # style="dashed"
                        )

        diagram.append("}")
        return "\n".join(diagram)

    def save_diagram(self, output_file="UML_Class_diagram.gv"):
        diagram_text = self.build_diagram()
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(diagram_text)
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

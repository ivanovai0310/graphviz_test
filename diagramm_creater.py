from code_analyzer import PythonStaticAnalyzer


class GraphvizDiagramBuilder:
    def __init__(self, model):
        self.model = model

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

        # Создание узлов для каждого класса
        for class_info in self.model:
            methods = '<br align="left"/>'.join(
                f"+ {method.name}()" for method in class_info.methods
            )
            methods_section = methods if methods else "No methods"
            label = (
                f'<{{<b>{class_info.name}</b>|{methods_section}<br align="left"/>}}>'
            )
            diagram.append(f"\t{class_info.name} [label={label}];")

        # Добавление связей для представления отношений наследования
        for class_info in self.model:
            for parent in class_info.parents:
                diagram.append(
                    f'\t{class_info.name} -> {parent} [dir="back" arrowtail="empty" style=""];'
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
    analyzer = PythonStaticAnalyzer('')
    analyzer.generate_test_data()
    model = analyzer.get_model()

    # Создание и сохранение UML-диаграммы в формате .gv
    diagram_builder = GraphvizDiagramBuilder(model)
    diagram_builder.save_diagram("UML_Class_diagram.gv")

import subprocess
from code_analyzer import PythonStaticAnalyzer
from diagramm_creater import GraphvizDiagramBuilder


if __name__ == "__main__":
    # Analyze the folder and get the model
    analyzer = PythonStaticAnalyzer(
        "/Users/aleksejivanov/PycharmProjects/synonym-soft/itb-synonym-core/src"
    )
    # analyzer.generate_test_data()
    analyzer.analyze()
    model = analyzer.get_model()

    # Build and render the Graphviz diagram
    diagram_builder = GraphvizDiagramBuilder(model)
    diagram_builder.build_diagram()
    diagram_builder.save_diagram()
    # diagram_builder.render_diagram("uml_output_file")

    subprocess.run(
        ["dot", "-Tpng", "UML_Class_diagram.gv", "-o", "UML_Class_diagram.png"]
    )

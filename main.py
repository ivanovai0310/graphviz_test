import subprocess
from code_analyzer import PythonStaticAnalyzer
from diagramm_creater import GraphvizDiagramBuilder, Modes

"""
    https://github.com/ivanovai0310/graphviz_test
"""


if __name__ == "__main__":
    # Analyze the folder and get the model
    analyzer = PythonStaticAnalyzer(
        # "/Users/aleksejivanov/PycharmProjects/nt-core/src/gui"
        # "/Users/aleksejivanov/PycharmProjects/synonym-soft/itb-synonym-core/src/filetransfer"
        "/Users/aleksejivanov/PycharmProjects/synonym-soft/itb-synonym-core/src/filetransfer"
    )
    # analyzer.generate_test_data()
    analyzer.analyze()
    model = analyzer.get_model()
    analyzer.save_model_to_json("anylyzer.json")

    # Build and render the Graphviz diagram
    diagram_builder = GraphvizDiagramBuilder(model, Modes.TRACER)
    diagram_builder.build_diagram()
    diagram_builder.save_diagram()
    diagram_builder.save_diagram_png()

    # diagram_builder.save_diagram_pdf()
    # diagram_builder.save_diagram_svg()

    # subprocess.run(
    #     ["dot", "-Tpng", "UML_Class_diagram.gv", "-o", "UML_Class_diagram.png"]
    # )

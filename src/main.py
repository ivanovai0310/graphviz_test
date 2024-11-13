import subprocess
from src.code_analyzer import PythonStaticAnalyzer
from src.diagramm_creater import GraphvizDiagramBuilder, Modes
from src.tracer_analyzer import TracerAnalyzer

"""
    https://github.com/ivanovai0310/graphviz_test
"""


if __name__ == "__main__":

    mode = Modes.TRACER
    # Analyze the folder and get the model
    analyzer = PythonStaticAnalyzer(
        # "/Users/aleksejivanov/PycharmProjects/nt-core/src/gui"
        # "/Users/aleksejivanov/PycharmProjects/synonym-soft/itb-synonym-core/src/filetransfer"
        "/Users/aleksejivanov/PycharmProjects/synonym-soft/itb-synonym-core/src"
    )
    # analyzer.generate_test_data()
    analyzer.analyze()

    if mode == Modes.TRACER:
        with open("examples/trace.txt", encoding="utf-8") as f:
            log = f.read()

        tracer_obj = TracerAnalyzer(log)
        tracers = tracer_obj.parse()
        analyzer.filter_model_by_tracer(tracers)
        pass

    analyzer.save_model_to_json("anylyzer.json")
    model = analyzer.get_model()

    # diagram_builder.save_diagram_pdf()

    # Build and render the Graphviz diagram
    diagram_builder = GraphvizDiagramBuilder(model, mode)
    diagram_builder.build_diagram()
    diagram_builder.save_diagram()
    diagram_builder.save_diagram_png()

    # diagram_builder.save_diagram_svg()

    # subprocess.run(
    #     ["dot", "-Tpng", "UML_Class_diagram.gv", "-o", "UML_Class_diagram.png"]
    # )

import subprocess
from typing import List
from tracer_analyzer import Tracer


# Class for generating PlantUML sequence diagrams from Tracers
class PlantUMLGenerator:
    def __init__(self, tracers: List[Tracer]):
        # Сохраняем только те трассировки, где есть имя класса и метода
        self.tracers = [t for t in tracers if t.class_name and t.method_name]

    def generate_sequence_diagram(self, output_file: str):
        # Generate .puml file
        with open(output_file, "w") as f:
            f.write("@startuml\n\n")

            # Define actors/participants with class.method format
            participants = set()
            for tracer in self.tracers:
                participants.add(tracer.class_name)

            for participant in participants:
                f.write(f'participant "{participant}" as {participant}\n')

            f.write("\n")

            # Track previous method for creating arrows on method change
            previous_lifeline = None
            for tracer in self.tracers:
                current_lifeline = f"{tracer.class_name}.{tracer.method_name}"

                # If the current method is different from the previous one, draw an arrow
                if previous_lifeline and previous_lifeline != current_lifeline:
                    # Extract class names for the arrow (class.method)
                    prev_class, _ = previous_lifeline.split(".")
                    curr_class, _ = current_lifeline.split(".")
                    f.write(f"{prev_class} -> {curr_class} : {tracer.method_name}()\n")

                # Update the previous method
                previous_lifeline = current_lifeline

            f.write("\n@enduml\n")

    def generate_png(self, puml_file: str):
        # Use PlantUML to convert the .puml file to .png
        try:
            subprocess.run(["plantuml", "-tpng", puml_file], check=True)
            print(f"PNG image generated for {puml_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error generating PNG: {e}")


# Example usage
if __name__ == "__main__":
    from tracer_analyzer import TracerAnalyzer

    # Открываем лог по новому пути
    with open("examples/trace.txt", encoding="utf-8") as f:
        log = f.read()

    analyzer = TracerAnalyzer(log)
    tracers = analyzer.parse()

    # Generate PlantUML diagram and PNG image
    generator = PlantUMLGenerator(tracers)
    puml_file = "trace_diagram.puml"
    generator.generate_sequence_diagram(puml_file)
    generator.generate_png(puml_file)

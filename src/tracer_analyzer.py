import re
from typing import List, Optional


# Model Tracer to store data
class Tracer:
    def __init__(self, raw_text: str, class_name: Optional[str] = None, method_name: Optional[str] = None):
        self.raw_text = raw_text
        self.class_name = class_name
        self.method_name = method_name

    def __repr__(self):
        return f"Tracer(raw_text={self.raw_text!r}, class_name={self.class_name!r}, method_name={self.method_name!r})"


# Class for log analysis
class TracerAnalyzer:
    def __init__(self, log: str):
        self.log = log
        self.class_method_pattern = re.compile(
            r"Entering class: (?P<class>\w+), function: (?P<method>\w+)"
        )

    def parse(self) -> List[Tracer]:
        tracers = []
        for line in self.log.splitlines():
            match = self.class_method_pattern.search(line)
            if match:
                # Create a Tracer object with class and method details
                class_name = match.group("class")
                method_name = match.group("method")
                tracer = Tracer(
                    raw_text=line, class_name=class_name, method_name=method_name
                )
            else:
                # Create a Tracer object with only the raw text
                tracer = Tracer(raw_text=line)
            tracers.append(tracer)
        return tracers


if __name__=="__main__":
# Example usage

    with open("src/examples/trace.txt", encoding="utf-8") as f:
        log = f.read()

    analyzer = TracerAnalyzer(log)
    tracers = analyzer.parse()

    # Print results
    for tracer in tracers:
        print(tracer)

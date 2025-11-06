import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Place:
    id: str
    name: Optional[str] = None
    initial_marking: int = 0

@dataclass
class Transition:
    id: str
    name: Optional[str] = None

@dataclass
class Arc:
    id: str
    source: str
    target: str

class PetriNet:
    def __init__(self):
        self.places: Dict[str, Place] = {}
        self.transitions: Dict[str, Transition] = {}
        self.arcs: List[Arc] = []

    def add_place(self, p: Place):
        if p.id in self.places:
            raise ValueError(f"Duplicate place id: {p.id}")
        self.places[p.id] = p

    def add_transition(self, t: Transition):
        if t.id in self.transitions:
            raise ValueError(f"Duplicate transition id: {t.id}")
        self.transitions[t.id] = t

    def add_arc(self, a: Arc):
        self.arcs.append(a)

    def check_consistency(self):
        errors, warnings = [], []
        for a in self.arcs:
            if a.source not in self.places and a.source not in self.transitions:
                errors.append(f"Arc {a.id} has unknown source {a.source}")
            if a.target not in self.places and a.target not in self.transitions:
                errors.append(f"Arc {a.id} has unknown target {a.target}")
        for p in self.places.values():
            if p.initial_marking not in (0, 1):
                warnings.append(f"Place {p.id} has marking {p.initial_marking} (not 0/1)")
        return errors, warnings

def strip_ns(tag: str):
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag

def parse_pnml(file_path: str) -> PetriNet:
    tree = ET.parse(file_path)
    root = tree.getroot()
    net = PetriNet()
    for elem in root.iter():
        tag = strip_ns(elem.tag)
        if tag == "place":
            pid = elem.attrib["id"]
            name, init = None, 0
            for c in elem:
                if strip_ns(c.tag) == "name":
                    for t in c.iter():
                        if strip_ns(t.tag) == "text":
                            name = t.text.strip()
                if "initialmarking" in strip_ns(c.tag).lower():
                    for t in c.iter():
                        if strip_ns(t.tag) == "text":
                            init = int(t.text.strip())
            net.add_place(Place(pid, name, init))
        elif tag == "transition":
            tid = elem.attrib["id"]
            name = None
            for c in elem.iter():
                if strip_ns(c.tag) == "text":
                    name = c.text.strip()
            net.add_transition(Transition(tid, name))
        elif tag == "arc":
            net.add_arc(Arc(elem.attrib["id"], elem.attrib["source"], elem.attrib["target"]))
    return net

def summary(net: PetriNet):
    print("=== Petri Net Summary ===")
    print(f"Places: {len(net.places)}")
    print(f"Transitions: {len(net.transitions)}")
    print(f"Arcs: {len(net.arcs)}")
    print("\nPlaces with initial marking = 1:")
    for p in net.places.values():
        if p.initial_marking == 1:
            print(f" - {p.id} ({p.name})")
    errors, warnings = net.check_consistency()
    if errors: print("\nErrors:", *errors, sep="\n  ")
    if warnings: print("\nWarnings:", *warnings, sep="\n  ")
    if not errors and not warnings: print("\nNo errors or warnings detected.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pnml_parser.py model.pnml")
        sys.exit(1)
    pn = parse_pnml(sys.argv[1])
    summary(pn)

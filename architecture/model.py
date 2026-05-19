from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Module:
    name: str
    input: str
    output: str
    description: str = ""


@dataclass
class Pipeline:
    name: str
    modules: List[str]


@dataclass
class Architecture:
    name: str
    types: List[str]
    modules: Dict[str, Module]
    pipelines: Dict[str, Pipeline]


@dataclass
class SemanticNode:
    name: str
    role: str
    description: str
    exports: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)


@dataclass
class RepositorySemanticModel:
    system_name: str
    nodes: dict[str, SemanticNode]
    global_constraints: list[str] = field(default_factory=list)
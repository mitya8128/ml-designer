from dataclasses import dataclass, field


@dataclass
class GenerationState:
    semantic_model: object
    generated_modules: dict = field(default_factory=dict)
    semantic_summaries: dict = field(default_factory=dict)
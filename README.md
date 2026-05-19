# ml-designer

**ml-designer** is a prototype system for generating, verifying, and implementing software architectures using LLMs and formal methods.

Instead of directly generating code from prompts, the system introduces an intermediate **Architecture DSL**, enabling:

* Structural validation
* Type checking
* Iterative refinement
* Future formal verification



## 🧠 Core Idea

"Traditional" approach:

```text
prompt → code
```

This project:

```text
prompt → architecture (DSL) → verification → code
```

This enables **more reliable, interpretable, and verifiable software generation**.



## 📦 Project Structure

```text
analyzer/
    code_metrics.py
    main_pipeline.py
    matching.py
    parser.py
    side_effects.py

architecture/
    loader.py
    model.py

llm/
    __init__.py
    base.py
    claude_client.py
    factory.py
    ollama_client.py
    openai_client.py

pipelines/
    repo_pipeline.py
    stages/
        repair_stage.py
        semantic_stage.py
        syntax_stage.py

prompts/
    code_generation_prompts.py
    rebuild_arch_prompts.py

utils/
    yaml_utils.py

verifier/
    rules.py
    verifier.py

sessions/
    architecture.yaml
    generated_code.py
    
README.md
main.py
requirements.txt
system.prompt
```



## ⚙️ Architecture DSL

Example:

```yaml
system:
  name: calendar_app

types:
  - Date
  - Event

modules:
  create_event:
    input: Event
    output: Event

  format_date:
    input: Date
    output: Date

pipelines:
  event_pipeline:
    - create_event
```



## 🧪 Code Verification 

The system includes AST-based analysis and verification:

* Function extraction
* Import/dependency analysis
* Repository-wide analysis
* Semantic contract verification
* Architecture consistency checks



## 🔁 Iterative Repair Loop

The system automatically:

```text
generate → verify → repair → repeat
```

until a valid architecture is produced.



## 🏗️ Repository-Level Generation

The system supports both:
- single-file generation
- repository-wide generation

Repository mode compiles the architecture into multiple semantic modules and generates them independently.

Pipeline:

```text
architecture (DSL)
    ↓
repository generation
    ↓
module verification
    ↓
repair loop
```

Each module is verified against its architectural contract and refined iteratively.



## ⚠️ Errors vs Warnings

The verifier distinguishes between:

### Errors
Hard architectural violations:
- missing required exports
- invalid semantic contracts
- interface mismatches

Errors trigger automatic repair.

### Warnings
Non-fatal architectural drift:
- unexpected external dependencies
- additional frameworks/libraries
- non-critical structural deviations

Warnings are logged but do not trigger repair.

This separation helps stabilize repository-level generation and avoids infinite repair loops caused by noisy LLM outputs.



## 🤖 LLM Integration

Currently supported:

* Ollama (local models)

Planned:

* OpenAI API
* Anthropic
* Multi-model pipelines





## 🚀 Usage

### Run the system

```bash
# full list of arguments:
python main.py -h

# full pipeline:
python main.py --prompt "calendar backend"

# full pipeline (example with ollama):
python main.py --provider ollama --model deepseek-r1 --prompt "calendar backend"

# use existing architecture:
python main.py --from-arch --arch my.yaml

# analyze existing pair:
python main.py --from-arch --no-code --arch arch.yaml --code code.py

# only analyze code:
python main.py --analyze-only --code app.py

# analyze whole repository:
python main.py --repo <path_to_repository>

# repository-level generation:
python main.py \
    --mode repository \
    --provider ollama \
    --model gemma3:latest \
    --prompt "Build a simple todo REST backend"
```

This will (a full pipeline):

1. Generate architecture via LLM
2. Normalize YAML
3. Verify architecture
4. Repair if needed
5. Generate Python code
6. Analyze generated code




## 🧩 Long-term Vision

The long-term direction of this project is not “bigger prompts”, but a transition from probabilistic code generation toward systems grounded in formal structure, semantics, and verification.

The framework explores an architecture-first approach where local language models generate code incrementally under continuous structural and semantic validation.

LLMs are treated primarily as compressed knowledge and synthesis engines — while architecture, static analysis, and formal constraints provide consistency and guarantees.

A major focus of the project is enabling practical software synthesis with small local models, including offline and CPU-based inference, through decomposition, repository-wide reasoning, and iterative verification.

This project explores:

* Architecture as IR (Intermediate Representation)
* AI-assisted software design
* Formal verification + LLMs
* Autonomous system design 


## 👨‍💻 Author

Dmitriy Akhmediyev



## 📄 License

TBD
import os
from .imports import extract_imports
from .matching import check_cycles, check_unused_functions, check_missing_functions
from .parser import extract_functions, extract_calls


def build_module_index(files):

    index = {}
    for path in files:
        module = os.path.splitext(os.path.basename(path))[0]
        index[module] = path

    return index


def collect_python_files(root_path):
    
    py_files = []

    for root, _, files in os.walk(root_path):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))

    return py_files


def parse_repository(files):

    all_functions = {}
    all_calls = {}
    all_imports = {}

    for file_path in files:
        try:
            with open(file_path) as f:
                code = f.read()
        except Exception:
            continue

        functions = extract_functions(code, file_path)
        calls = extract_calls(code)
        imports = extract_imports(code)

        # namespace functions
        for name, meta in functions.items():
            key = f"{file_path}::{name}"
            all_functions[key] = meta

        all_calls[file_path] = calls
        all_imports[file_path] = imports

    return all_functions, all_calls, all_imports


def build_global_call_graph(all_functions, all_calls, 
                            all_imports, module_index):

    graph = {f: [] for f in all_functions.keys()}

    # full function index
    function_index = {}

    for full_name in all_functions:
        file_path, func = full_name.split("::")
        function_index[(file_path, func)] = full_name

    # resolve calls
    for file_path, calls in all_calls.items():
        imports = all_imports.get(file_path, {})
        for caller, callee in calls:
            caller_key = function_index.get((file_path, caller))

            if caller_key is None:
                continue
            resolved = None

            # imported symbol
            if callee in imports:
                imp = imports[callee]
                module_name = imp["module"]
                target_file = module_index.get(module_name)

                if target_file:
                    resolved = function_index.get((target_file, callee))

            # local fallback
            if resolved is None:
                resolved = function_index.get((file_path, callee))

            if resolved:
                graph[caller_key].append(resolved)

    return graph


def analyze_repository(root_path):

    files = collect_python_files(root_path)
    all_functions, all_calls, all_imports = parse_repository(files)
    module_index = build_module_index(files)
    graph = build_global_call_graph(all_functions, all_calls, 
                                    all_imports, module_index)

    errors = []
    warnings = []

    errors += check_missing_functions(graph)
    errors += check_cycles(graph)
    errors += check_unused_functions(graph)

    metrics = {
        "num_files": len(files),
        "num_functions": len(all_functions),
        "num_edges": sum(len(v) for v in graph.values()),
        "num_errors": len(errors),
        "num_warnings": len(warnings),
    }

    return {
        "graph": graph,
        "functions": all_functions,
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
    }
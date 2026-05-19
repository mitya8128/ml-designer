from architecture.model import SemanticNode,RepositorySemanticModel


def compile_semantic_model(arch):
    
    nodes = {}
    
    for module_name, module in arch.modules.items():
        node = SemanticNode(name=module.name,
                            role=getattr(module, "role", "service"),
                            description=getattr(module, "description", ""), 
                            exports=getattr(module, "exports", []),
                            depends_on=getattr(module, "depends_on", []), 
                            constraints=getattr(module, "constraints", []))

        nodes[module.name] = node

    return RepositorySemanticModel(system_name= "", 
                                   nodes=nodes,
                                   global_constraints=getattr(arch,"global_constraints",[]))
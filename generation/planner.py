from collections import defaultdict, deque


def compute_generation_order(model):

    indegree = defaultdict(int)
    graph = defaultdict(list)

    for node in model.nodes.values():

        for dep in node.depends_on:

            graph[dep].append(node.name)
            indegree[node.name] += 1

        if node.name not in indegree:
            indegree[node.name] = indegree[node.name]

    queue = deque()

    for node_name, degree in indegree.items():
        if degree == 0:
            queue.append(node_name)

    result = []

    while queue:

        current = queue.popleft()
        result.append(current)

        for nxt in graph[current]:
            indegree[nxt] -= 1

            if indegree[nxt] == 0:
                queue.append(nxt)

    return result
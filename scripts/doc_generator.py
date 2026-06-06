import json
import os
import re

def generate_mermaid_diagram(graph):
    """Generate a high-level module dependency graph dynamically."""
    mermaid = ["```mermaid", "graph TD"]

    nodes = set()
    edges = set()

    discovered_roots = graph.get("discovered_roots", [])

    for module_path, imports in graph.get("modules", {}).items():
        module_dir = os.path.dirname(module_path).split(os.sep)[0]
        if not module_dir or module_dir not in discovered_roots:
            continue

        nodes.add(module_dir)

        for imp in imports:
            # Common stdlib to ignore
            if imp in ["os", "sys", "json", "typing", "ast", "re", "logging", "asyncio", "pathlib", "collections", "datetime"]:
                continue

            # If the import matches one of our dynamic roots, link it internally
            if imp in discovered_roots:
                edges.add((module_dir, imp))
            else:
                nodes.add("External_Dependencies")
                edges.add((module_dir, "External_Dependencies"))

    for node in sorted(nodes):
        mermaid.append(f"  {node}")

    for src, dst in sorted(edges):
        if src != dst:
            mermaid.append(f"  {src} --> {dst}")

    mermaid.append("```")
    return "\n".join(mermaid)

def generate_dynamic_tech_stack(graph):
    """Generate a simple list of external dependencies detected via imports."""
    discovered_roots = graph.get("discovered_roots", [])
    external_deps = set()

    for imports in graph.get("modules", {}).values():
        for imp in imports:
            if imp not in discovered_roots and imp not in ["os", "sys", "json", "typing", "ast", "re", "logging", "asyncio", "pathlib", "collections", "datetime"]:
                external_deps.add(imp)

    if not external_deps:
        return "*No external dependencies detected.*"

    return ", ".join([f"`{dep}`" for dep in sorted(list(external_deps))[:15]]) + " (and others)"


def update_readme(mermaid_diagram, tech_stack):
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = "# OpenEnv\n\n"

    diagram_section = f"\n<!-- ARCHITECTURE_START -->\n## Architecture Overview\n\n{mermaid_diagram}\n\n### Detected Tech Stack\n{tech_stack}\n\n*Note: This architecture overview is continuously updated by the AI Doc Agent.*\n<!-- ARCHITECTURE_END -->\n"

    if "<!-- ARCHITECTURE_START -->" in content:
        content = re.sub(r"<!-- ARCHITECTURE_START -->[\s\S]*?<!-- ARCHITECTURE_END -->", diagram_section, content)
    else:
        # Append to the end
        content += diagram_section

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    try:
        with open("repo_graph.json", "r", encoding="utf-8") as f:
            graph = json.load(f)

        diagram = generate_mermaid_diagram(graph)
        stack = generate_dynamic_tech_stack(graph)
        update_readme(diagram, stack)
        print("Documentation generation complete.")

    except FileNotFoundError:
        print("repo_graph.json not found. Run repo_analyzer.py first.")

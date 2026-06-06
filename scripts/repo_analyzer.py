import os
import ast
import json

IGNORED_DIRS = {".git", ".github", ".venv", "venv", "__pycache__", "build", "dist", "node_modules", "docs", ".pytest_cache", ".agents", ".claude"}

def analyze_repo_dynamic():
    """Dynamically discover root modules and map basic imports."""
    repo_graph = {
        "modules": {},
        "discovered_roots": []
    }

    # Discover top-level non-ignored, non-file items
    root_dirs = []
    for item in os.listdir("."):
        if os.path.isdir(item) and item not in IGNORED_DIRS and not item.startswith("."):
            root_dirs.append(item)

    repo_graph["discovered_roots"] = root_dirs

    for root_dir in root_dirs:
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = os.path.join(root, file)
                    rel_file_path = os.path.relpath(file_path, start=".")

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        tree = ast.parse(content)
                        imports = []

                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    imports.append(alias.name.split('.')[0])
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    imports.append(node.module.split('.')[0])

                        # Only keep unique external/internal top-level dependencies
                        repo_graph["modules"][rel_file_path] = list(set(imports))
                    except Exception:
                        pass # Silently skip errors for resilience

    return repo_graph

if __name__ == "__main__":
    graph = analyze_repo_dynamic()

    with open("repo_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print("Dynamic repository analysis complete. Graph saved to repo_graph.json")

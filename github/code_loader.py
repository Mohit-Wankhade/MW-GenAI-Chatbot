import os
SUPPORTED_EXTENSIONS = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".md"]

def load_code_files(repo_path,repo_name):
    files = []
    for root, dirs, filenames in os.walk(repo_path):
        for file in filenames:
            if any(file.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    files.append({"repo":repo_name, "file": file, "path": path, "content": content})
                except:
                    pass
    return files
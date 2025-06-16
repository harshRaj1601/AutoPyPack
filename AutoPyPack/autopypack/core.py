import sys
import subprocess
import ast
import json
import os
import importlib.util

def load_mappings():
    path = os.path.join(os.path.dirname(__file__), "mappings.json")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[AutoPyPack] Warning: Could not find mappings.json at {path}")
        return {}

install_name_mapping = load_mappings()

def install_package(package_name, quiet=False):
    try:
        if not quiet:
            print(f"[AutoPyPack] Installing: {package_name} ...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package_name],
            stdout=subprocess.DEVNULL if quiet else None,
            stderr=subprocess.DEVNULL if quiet else None
        )
        return True
    except subprocess.CalledProcessError:
        if not quiet:
            print(f"[AutoPyPack] ❌ Failed to install {package_name}. Please install manually.")
        return False

def is_module_available(module_name):
    """Check if a module is available in the current Python environment."""
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ModuleNotFoundError, ValueError):
        return False

def scan_imports(file_path):
    """
    Scan a Python file for import statements and return a set of imported module names.
    
    Args:
        file_path (str): Path to the Python file to scan
        
    Returns:
        set: Set of imported module names
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except Exception as e:
        print(f"[AutoPyPack] Error reading {file_path}: {str(e)}")
        return set()
        
    try:
        node = ast.parse(content, filename=file_path)
    except SyntaxError as e:
        print(f"[AutoPyPack] Syntax error in {file_path}: {str(e)}")
        return set()

    imported_modules = set()

    for n in ast.walk(node):
        if isinstance(n, ast.Import):
            for alias in n.names:
                # Only add the module if it's actually imported
                # This checks if the import statement exists in the file
                imported_modules.add(alias.name.split('.')[0])
        elif isinstance(n, ast.ImportFrom):
            if n.module:
                # Only add the module if it's actually imported from
                # This checks if the import from statement exists in the file
                imported_modules.add(n.module.split('.')[0])

    return imported_modules

def main():
    """Legacy function for backward compatibility."""
    if len(sys.argv) < 2:
        print("[AutoPyPack] Error: No file specified.")
        print("[AutoPyPack] Usage: python -m autopypack <file.py>")
        return
        
    script_path = sys.argv[1]
    if not os.path.exists(script_path):
        print(f"[AutoPyPack] Error: File not found: {script_path}")
        return
        
    print(f"[AutoPyPack] Scanning file: {script_path}")
    modules = scan_imports(script_path)
    
    if not modules:
        print("[AutoPyPack] No imports found.")
        return
        
    print(f"[AutoPyPack] Found {len(modules)} imports.")
    
    for mod in modules:
        if not is_module_available(mod):
            install_name = install_name_mapping.get(mod, mod)
            install_package(install_name)
            
    print("[AutoPyPack] Done!") 
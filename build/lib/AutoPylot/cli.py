import argparse
import os
import sys
import pkgutil
from .core import scan_imports, is_module_available, install_package, load_mappings

def find_python_files(directory):
    """Recursively find all Python files in the directory."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def collect_all_imports(directory):
    """Scan all Python files in the directory and collect imports."""
    python_files = find_python_files(directory)
    all_imports = set()
    
    print(f"[AutoPylot] Scanning {len(python_files)} Python files for imports...")
    
    for file_path in python_files:
        try:
            imports = scan_imports(file_path)
            all_imports.update(imports)
        except Exception as e:
            print(f"[AutoPylot] Error scanning {file_path}: {str(e)}")
    
    return all_imports

def is_stdlib_module(module_name):
    """Check if a module is part of the Python standard library."""
    if module_name in sys.builtin_module_names:
        return True
    
    # Check if module is in stdlib paths
    for path in sys.path:
        if path.endswith('site-packages') or path.endswith('dist-packages'):
            continue
        
        if os.path.exists(os.path.join(path, module_name)) or os.path.exists(os.path.join(path, module_name + '.py')):
            return True
    
    # Common standard library modules that might not be caught by the above checks
    stdlib_modules = [
        'os', 'sys', 're', 'math', 'random', 'datetime', 'time', 'json', 'pickle', 
        'collections', 'functools', 'itertools', 'typing', 'pathlib', 'io', 'argparse', 
        'logging', 'threading', 'multiprocessing', 'subprocess', 'tempfile', 'shutil', 
        'glob', 'fnmatch', 'socket', 'email', 'mimetypes', 'base64', 'hashlib', 'hmac', 
        'uuid', 'unittest', 'ast', 'inspect', 'importlib', 'signal', 'asyncio', 'csv', 
        'xml', 'html', 'urllib', 'http', 'ftplib', 'ssl', 'zlib', 'zipfile', 'tarfile',
        'platform', 'traceback', 'gc', 'operator', 'contextlib', 'copy', 'struct',
        'configparser', 'warnings', 'statistics', 'decimal', 'fractions', 'enum', 'array',
        'bisect', 'heapq', 'queue', 'weakref', 'abc', 'calendar','tkinter','turtle'
    ]
    
    return module_name in stdlib_modules

def install_missing_packages(directory):
    """Install missing packages for all imports found in the directory."""
    mappings = load_mappings()
    all_imports = collect_all_imports(directory)
    
    if not all_imports:
        print("[AutoPylot] No imports found in the project.")
        return
    
    print(f"[AutoPylot] Found {len(all_imports)} unique imports.")
    
    # Get project directory name to exclude internal modules
    project_name = os.path.basename(os.path.abspath(directory))
    internal_modules = ['autopylot', 'AutoPylot', 'core', 'cli', project_name.lower()]
    
    missing_packages = []
    for module_name in all_imports:
        # Skip internal modules and standard library modules
        if module_name in internal_modules or is_stdlib_module(module_name):
            continue
            
        # Skip if module is already available
        if not is_module_available(module_name):
            package_name = mappings.get(module_name, module_name)
            missing_packages.append((module_name, package_name))
    
    if not missing_packages:
        print("[AutoPylot] All packages are already installed! ✅")
        return
    
    print(f"[AutoPylot] Found {len(missing_packages)} missing packages to install.")
    
    for module_name, package_name in missing_packages:
        install_package(package_name)
    
    print("[AutoPylot] Package installation complete! ✅")

def main():
    parser = argparse.ArgumentParser(description="AutoPylot - Automatically install missing Python packages")
    subparsers = parser.add_subparsers(dest="command")
    
    # Install command
    install_parser = subparsers.add_parser("install", aliases=["i"], help="Scan project and install missing packages")
    install_parser.add_argument("--dir", "-d", default=".", help="Directory to scan (default: current directory)")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command in ["install", "i"]:
        directory = os.path.abspath(args.dir)
        print(f"[AutoPylot] Scanning directory: {directory}")
        install_missing_packages(directory)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 
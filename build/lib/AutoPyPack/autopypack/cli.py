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

def collect_all_imports(directory, quiet=False):
    """Scan all Python files in the directory and collect imports."""
    python_files = find_python_files(directory)
    all_imports = set()
    
    if not quiet:
        print(f"[AutoPyPack] Scanning {len(python_files)} Python files for imports...")
    
    for file_path in python_files:
        try:
            imports = scan_imports(file_path)
            all_imports.update(imports)
        except Exception as e:
            if not quiet:
                print(f"[AutoPyPack] Error scanning {file_path}: {str(e)}")
    
    return all_imports

def is_local_module(module_name, directory):
    """Check if a module name refers to a local Python file or directory in the project."""
    # Check if there's a .py file with this name
    py_file = os.path.join(directory, f"{module_name}.py")
    if os.path.isfile(py_file):
        return True
    
    # Check if there's a directory with this name (might be a package)
    dir_path = os.path.join(directory, module_name)
    if os.path.isdir(dir_path):
        # Check if it has an __init__.py to confirm it's a package
        init_file = os.path.join(dir_path, "__init__.py")
        if os.path.isfile(init_file):
            return True
        
        # Even without __init__.py, if there are Python files inside, consider it local
        for _, _, files in os.walk(dir_path):
            if any(f.endswith('.py') for f in files):
                return True
    
    # Recursively check in subdirectories
    for root, dirs, _ in os.walk(directory):
        for d in dirs:
            # Check each subdirectory for module
            subdir_path = os.path.join(root, d)
            py_file = os.path.join(subdir_path, f"{module_name}.py")
            dir_path = os.path.join(subdir_path, module_name)
            
            if os.path.isfile(py_file):
                return True
            
            if os.path.isdir(dir_path):
                init_file = os.path.join(dir_path, "__init__.py")
                if os.path.isfile(init_file):
                    return True
                
                # Check for any Python files inside
                for _, _, files in os.walk(dir_path):
                    if any(f.endswith('.py') for f in files):
                        return True
    
    return False

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

def install_missing_packages(directory, quiet=False):
    """Install missing packages for all imports found in the directory."""
    mappings = load_mappings()
    all_imports = collect_all_imports(directory, quiet)
    
    if not all_imports:
        if not quiet:
            print("[AutoPyPack] No imports found in the project.")
        return
    
    if not quiet:
        print(f"[AutoPyPack] Found {len(all_imports)} unique imports.")
    
    # Get project directory name to exclude internal modules
    project_name = os.path.basename(os.path.abspath(directory))
    internal_modules = ['autopypack', 'AutoPyPack', 'core', 'cli', project_name.lower()]
    
    # Get the current module name to avoid considering it as a dependency
    current_module_name = os.path.basename(os.path.dirname(os.path.abspath(__file__))).lower()
    if current_module_name not in internal_modules:
        internal_modules.append(current_module_name)
    
    missing_packages = []
    for module_name in all_imports:
        # Skip internal modules and standard library modules
        if module_name.lower() in [m.lower() for m in internal_modules] or is_stdlib_module(module_name):
            continue
        
        # Skip if it's a local module in the project directory
        if is_local_module(module_name, directory):
            if not quiet:
                print(f"[AutoPyPack] Detected local module: {module_name}")
            continue
            
        # Skip if module is already available
        if not is_module_available(module_name):
            package_name = mappings.get(module_name, module_name)
            missing_packages.append((module_name, package_name))
    
    if not missing_packages:
        if not quiet:
            print("[AutoPyPack] All packages are already installed! ✅")
        return
    
    if not quiet:
        print(f"[AutoPyPack] Found {len(missing_packages)} missing packages to install.")
    
    for module_name, package_name in missing_packages:
        install_package(package_name, quiet)
    
    if not quiet:
        print("[AutoPyPack] Package installation complete! ✅")

def list_project_modules(directory, quiet=False):
    """List all non-standard library modules used in the project."""
    mappings = load_mappings()
    all_imports = collect_all_imports(directory, quiet)
    
    if not all_imports and not quiet:
        print("[AutoPyPack] No imports found in the project.")
        return []
    
    if not quiet:
        print(f"[AutoPyPack] Found {len(all_imports)} unique imports.")
    
    # Get project directory name to exclude internal modules
    project_name = os.path.basename(os.path.abspath(directory))
    internal_modules = ['autopypack', 'AutoPyPack', 'core', 'cli', project_name.lower()]
    
    # Get the current module name to avoid considering it as a dependency
    current_module_name = os.path.basename(os.path.dirname(os.path.abspath(__file__))).lower()
    if current_module_name not in internal_modules:
        internal_modules.append(current_module_name)
    
    external_packages = []
    for module_name in all_imports:
        # Skip internal modules and standard library modules
        if module_name.lower() in [m.lower() for m in internal_modules] or is_stdlib_module(module_name):
            continue
        
        # Skip if it's a local module in the project directory
        if is_local_module(module_name, directory):
            if not quiet:
                print(f"[AutoPyPack] Detected local module: {module_name}")
            continue
        
        package_name = mappings.get(module_name, module_name)
        if package_name not in external_packages:
            external_packages.append(package_name)
    
    external_packages.sort()  # Sort alphabetically for readability
    
    if not quiet:
        if not external_packages:
            print("[AutoPyPack] No external packages found.")
        else:
            print(f"[AutoPyPack] Found {len(external_packages)} external packages:")
            for package in external_packages:
                print(package)
    
    return external_packages

def main():
    parser = argparse.ArgumentParser(description="AutoPyPack - Automatically install missing Python packages")
    subparsers = parser.add_subparsers(dest="command")
    
    # Install command
    install_parser = subparsers.add_parser("install", aliases=["i"], help="Scan project and install missing packages")
    install_parser.add_argument("--dir", "-d", default=".", help="Directory to scan (default: current directory)")
    install_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress informational output")
    
    # List command
    list_parser = subparsers.add_parser("list", aliases=["l"], help="List all external packages used in the project")
    list_parser.add_argument("--dir", "-d", default=".", help="Directory to scan (default: current directory)")
    list_parser.add_argument("--quiet", "-q", action="store_true", help="Only output package names without additional info (good for redirecting to requirements.txt)")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command in ["install", "i"]:
        directory = os.path.abspath(args.dir)
        if not args.quiet:
            print(f"[AutoPyPack] Scanning directory: {directory}")
        install_missing_packages(directory, args.quiet)
    elif args.command in ["list", "l"]:
        directory = os.path.abspath(args.dir)
        if not args.quiet:
            print(f"[AutoPyPack] Scanning directory: {directory}")
        packages = list_project_modules(directory, args.quiet)
        if args.quiet and packages:
            # Print only package names, one per line (good for redirection to requirements.txt)
            for package in packages:
                print(package)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 
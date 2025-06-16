from .core import main, scan_imports, is_module_available, install_package, load_mappings
import sys
import os

class AutoPyPack:
    """
    AutoPyPack class for importing and using directly in Python files.
    Usage: import AutoPyPack
    """
    @staticmethod
    def install(directory="."):
        """
        Install missing packages for imports in the given directory.
        
        Args:
            directory (str): Directory to scan for Python files
        """
        from .cli import install_missing_packages
        directory = os.path.abspath(directory)
        print(f"[AutoPyPack] Scanning directory: {directory}")
        install_missing_packages(directory)
    
    @staticmethod
    def scan_file(file_path):
        """
        Scan a specific file for imports and install missing packages.
        
        Args:
            file_path (str): Path to the Python file to scan
        """
        from .core import scan_imports, is_module_available, install_package, load_mappings
        
        print(f"[AutoPyPack] Scanning file: {file_path}")
        mappings = load_mappings()
        
        try:
            imports = scan_imports(file_path)
            if not imports:
                print("[AutoPyPack] No imports found in the file.")
                return
                
            print(f"[AutoPyPack] Found {len(imports)} imports.")
            
            missing_packages = []
            for module_name in imports:
                # Skip standard library and internal modules
                if module_name in ('autopypack', 'AutoPyPack') or module_name in sys.builtin_module_names:
                    continue
                    
                # Check if module is available
                if not is_module_available(module_name):
                    package_name = mappings.get(module_name, module_name)
                    missing_packages.append((module_name, package_name))
            
            if not missing_packages:
                print("[AutoPyPack] All packages are already installed! ✅")
                return
                
            print(f"[AutoPyPack] Found {len(missing_packages)} missing packages to install.")
            
            for module_name, package_name in missing_packages:
                install_package(package_name)
                
            print("[AutoPyPack] Package installation complete! ✅")
                
        except Exception as e:
            print(f"[AutoPyPack] Error scanning {file_path}: {str(e)}")

# Create a global instance that can be imported
autopypack = AutoPyPack()

# Only auto-scan when directly imported by user code, not through the AutoPyPack.py bridge
# The bridge file will handle scanning for users importing via "import AutoPyPack"
if __name__ != "__main__":  # Not being run directly
    # Only auto-scan when imported directly from user code, not through the bridge
    caller_frame = sys._getframe(1)  # Get the frame of the caller
    if caller_frame:
        caller_module = caller_frame.f_globals.get('__name__', '')
        caller_file = caller_frame.f_code.co_filename
        
        # Only scan when directly imported by user code, not from AutoPyPack.py or internal modules
        if (not caller_module.startswith('autopypack') and 
            not caller_module == '__main__' and 
            not 'cli' in caller_module and
            not caller_file.endswith('AutoPyPack.py')):
            
            if os.path.exists(caller_file) and os.path.isfile(caller_file) and not caller_file.endswith('__init__.py'):
                AutoPyPack.scan_file(caller_file)
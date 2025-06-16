from .autopypack import AutoPyPack, autopypack
import sys
import os
import traceback
import inspect

# Re-export everything to make it accessible via import AutoPyPack
__all__ = ['AutoPyPack', 'autopypack']

# This allows methods to be called directly on the module:
# import AutoPyPack
# AutoPyPack.install()
install = AutoPyPack.install
scan_file = AutoPyPack.scan_file

# Debug flag
DEBUG = False

# Get calling script information
try:
    frame = sys._getframe(1)
    caller_file = frame.f_code.co_filename
    if DEBUG:
        print(f"[Debug] Initial caller: {caller_file}")
    
    # Walk up the call stack to find the original caller (the script being run)
    original_caller = None
    frame_num = 1
    while frame and frame_num < 10:  # Limit to 10 frames to avoid infinite loops
        if frame.f_code.co_filename not in ('<frozen importlib._bootstrap>', '<frozen importlib._bootstrap_external>'):
            original_caller = frame.f_code.co_filename
            if DEBUG:
                print(f"[Debug] Found original caller at frame {frame_num}: {original_caller}")
            break
        frame = frame.f_back
        frame_num += 1
        
    # If we found a valid calling script, scan it for imports
    if original_caller and os.path.isfile(original_caller) and not original_caller.endswith(('__init__.py', 'AutoPyPack.py')):
        if DEBUG or True:  # Always show this message
            print(f"[AutoPyPack] Auto-scanning imports in {os.path.basename(original_caller)}")
        scan_file(original_caller)
except Exception as e:
    if DEBUG:
        print(f"[Debug] Error in auto-scanning: {e}")
        traceback.print_exc()

# Auto-scanning of the importing script
# This will run when a script does "import AutoPyPack"
def _auto_scan():
    """Automatically scan the importing script for package dependencies."""
    try:
        # Get the stack frame that imported this module
        for frame_info in inspect.stack():
            # Skip frames from this module, internal imports, etc.
            if frame_info.filename.endswith(('AutoPyPack.py', '__init__.py')) or \
               '<frozen' in frame_info.filename or \
               frame_info.filename.startswith('<'):
                continue
            
            # Found the user script that imported this module
            if os.path.isfile(frame_info.filename):
                print(f"[AutoPyPack] Auto-scanning imports in {os.path.basename(frame_info.filename)}")
                # Directly call the scan_file function from autopypack module
                # This avoids any potential issues with the re-exported method
                autopypack.scan_file(frame_info.filename)
                break
    except Exception as e:
        print(f"[AutoPyPack] Error while auto-scanning: {e}")
        traceback.print_exc()

# Run the auto-scan when imported
if __name__ == "__main__":
    _auto_scan() 
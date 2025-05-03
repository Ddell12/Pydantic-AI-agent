"""
Code execution tools for the agent.

This module provides safe code execution functionality with appropriate security restrictions.
"""

from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_globals, safe_builtins, guarded_unpack_sequence
from typing import Dict, Any, List, Optional
import sys

def execute_safe_code_tool(code: str) -> str:
    """
    Executes a given Python code string in a protected environment.
    
    Args:
        code: Python code to execute
        
    Returns:
        str: Anything printed out to standard output with the print command
    """
    # Set up allowed modules
    allowed_modules = {
        # Core utilities
        'datetime': __import__('datetime'),
        'math': __import__('math'),
        'random': __import__('random'),
        'time': __import__('time'),
        'collections': __import__('collections'),
        'itertools': __import__('itertools'),
        'functools': __import__('functools'),
        'copy': __import__('copy'),
        're': __import__('re'),  # Regular expressions
        'json': __import__('json'),
        'csv': __import__('csv'),
        'uuid': __import__('uuid'),
        'string': __import__('string'),
        'statistics': __import__('statistics'),
        
        # Data structures and algorithms
        'heapq': __import__('heapq'),
        'bisect': __import__('bisect'),
        'array': __import__('array'),
        'enum': __import__('enum'),
        'dataclasses': __import__('dataclasses'),
        
        # Numeric/scientific (if installed)
        # 'numpy': __import__('numpy', fromlist=['*']),
        # 'pandas': __import__('pandas', fromlist=['*']),
        # 'scipy': __import__('scipy', fromlist=['*']),
        
        # File/IO (with careful restrictions)
        'io': __import__('io'),
        'base64': __import__('base64'),
        'hashlib': __import__('hashlib'),
        'tempfile': __import__('tempfile')
    }
    
    # Try to import optional modules that might not be installed
    try:
        allowed_modules['numpy'] = __import__('numpy')
    except ImportError:
        pass
        
    try:
        allowed_modules['pandas'] = __import__('pandas')
    except ImportError:
        pass
        
    try:
        allowed_modules['scipy'] = __import__('scipy')
    except ImportError:
        pass
    
    # Custom import function that only allows whitelisted modules
    def safe_import(name, *args, **kwargs):
        """
        Custom import function that only allows whitelisted modules.
        
        Args:
            name: Name of the module to import
            *args: Additional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            The imported module if it's in the allowed list
            
        Raises:
            ImportError: If the module is not in the allowed list
        """
        if name in allowed_modules:
            return allowed_modules[name]
        raise ImportError(f"Module {name} is not allowed")
    
    # Create a safe environment with minimal built-ins
    safe_builtins_dict = {
        # Basic operations
        'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool, 
        'chr': chr, 'complex': complex, 'divmod': divmod, 'float': float, 
        'format': format, 'hex': hex, 'int': int, 'len': len, 'max': max, 
        'min': min, 'oct': oct, 'ord': ord, 'pow': pow, 'round': round,
        'sorted': sorted, 'sum': sum,
        
        # Types and conversions
        'bytes': bytes, 'dict': dict, 'frozenset': frozenset, 'list': list, 
        'repr': repr, 'set': set, 'slice': slice, 'str': str, 'tuple': tuple, 
        'type': type, 'zip': zip,
        
        # Iteration and generation
        'enumerate': enumerate, 'filter': filter, 'iter': iter, 'map': map,
        'next': next, 'range': range, 'reversed': reversed,
        
        # Other safe operations
        'getattr': getattr, 'hasattr': hasattr, 'hash': hash,
        'isinstance': isinstance, 'issubclass': issubclass,
        
        # Import handler
        '__import__': safe_import
    }
    
    # Set up output capture
    output = []
    def safe_print(*args, **kwargs):
        """
        Custom print function that captures output to a list.
        
        Args:
            *args: Arguments to print
            **kwargs: Keyword arguments for print (only end and sep are supported)
            
        Returns:
            None
        """
        end = kwargs.get('end', '\n')
        sep = kwargs.get('sep', ' ')
        output.append(sep.join(str(arg) for arg in args) + end)
    
    # Create restricted globals
    restricted_globals = {
        '__builtins__': safe_builtins_dict,
        'print': safe_print
    }
    
    try:
        # Execute the code with timeout
        exec(code, restricted_globals)
        return ''.join(output)
    except Exception as e:
        return f"Error executing code: {str(e)}"

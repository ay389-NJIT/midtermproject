########################
# Operation Decorators #
########################

from typing import Dict, Any
from colorama import Fore, Style

class OperationRegistry:
    '''
    Registry for the operations (via decorator)
    This class records all data from the operations, so the use
    of a help menu can be automated.
    
    '''
    _operations: Dict[str, Dict[str,Any]] = {}

    @classmethod
    def register(clas, name: str, category: str, description: str, example: str = ""):
        """
        Decorator to register an operation with metadata.
        
        Args:
            name: Command name for the operation (e.g., 'add')
            category: Category for grouping (e.g., 'Basic Arithmetic')
            description: Human-readable description
            example: Usage example (optional)
            
        Example:
            @OperationRegistry.register('add', 'Basic', 'Addition of two numbers')
            class Addition(Operation):
                pass
        """
        def decorator(operation_class):
            cls._operations[name] = {
                'class': operation_class,
                'category': category,
                'description': description,
                'example': example,
                'name': name
            }
            return operation_class
        return decorator
    
    @classmethod
    def get_operations(cls) -> Dict[str, Dict[str, Any]]:
        """Get all registered operations."""
        return cls._operations.copy()
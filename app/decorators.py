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
    def register(cls, name: str, category: str, description: str, example: str = ""):
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
    
    @classmethod
    def get_by_category(cls) -> Dict[str, list]:
        """
        Group operations by category for organized display.
        
        Returns:
            Dictionary mapping category names to lists of operations
        """
        categories = {}
        for op_name, op_data in cls._operations.items():
            category = op_data['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(op_data)
        return categories
    
    @classmethod
    def get_operation_names(cls) -> list:
        """Get list of all operation command names."""
        return list(cls._operations.keys())
    
    @classmethod
    def generate_help_text(cls) -> str:
        """
        Dynamically generate help menu text from registered operations.
        
        Returns:
            Formatted help text with all operations organized by category
        """

        help_lines = [f"\n{Fore.CYAN}Available commands:{Style.RESET_ALL}\n"]
        
        # Group operations by category
        categories = cls.get_by_category()
        
        # Define category order for display
        category_order = [
            'Basic Arithmetic',
            'Advanced Operations',
            'Specialized Operations'
        ]
        
        # Display operations by category
        for category in category_order:
            if category in categories:
                help_lines.append(f"{Fore.YELLOW}{category}:{Style.RESET_ALL}")
                for op in categories[category]:
                    help_lines.append(
                        f"  {Fore.GREEN}{op['name']:<12}{Style.RESET_ALL} - {op['description']}"
                    )
                help_lines.append("")  # Blank line between categories
        
        # Add utility commands
        help_lines.append(f"{Fore.YELLOW}History Management:{Style.RESET_ALL}")
        help_lines.append(f"  {Fore.CYAN}history{Style.RESET_ALL}      - Show calculation history")
        help_lines.append(f"  {Fore.CYAN}clear{Style.RESET_ALL}        - Clear calculation history")
        help_lines.append(f"  {Fore.CYAN}undo{Style.RESET_ALL}         - Undo the last calculation")
        help_lines.append(f"  {Fore.CYAN}redo{Style.RESET_ALL}         - Redo the last undone calculation")
        help_lines.append(f"  {Fore.CYAN}save{Style.RESET_ALL}         - Save calculation history to file")
        help_lines.append(f"  {Fore.CYAN}load{Style.RESET_ALL}         - Load calculation history from file")
        help_lines.append("")
        
        help_lines.append(f"{Fore.YELLOW}Utility:{Style.RESET_ALL}")
        help_lines.append(f"  {Fore.MAGENTA}help{Style.RESET_ALL}         - Display this help menu")
        help_lines.append(f"  {Fore.MAGENTA}exit{Style.RESET_ALL}         - Exit the calculator")
        
        return "\n".join(help_lines)
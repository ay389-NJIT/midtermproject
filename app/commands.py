########################
# Command Pattern      #
########################

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, List
import logging
from datetime import datetime

from app.calculator import Calculator
from app.operations import OperationFactory


class Command(ABC):
    """
    Abstract base class for commands using the Command pattern.
    
    Encapsulates a request as an object, allowing for parameterization,
    queuing, logging, and undo/redo of operations.
    """
    
    @abstractmethod
    def execute(self) -> Optional[Decimal]:
        """Execute the command."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get human-readable description of the command."""
        pass


class CalculationCommand(Command):
    """
    Command that encapsulates a calculation operation.
    
    This allows calculations to be queued, logged, and potentially
    replayed or undone.
    """
    
    def __init__(self, calculator: Calculator, operation_name: str, 
                 operand1: str, operand2: str):
        """
        Initialize calculation command.
        
        Args:
            calculator: Calculator instance to execute on
            operation_name: Name of operation (e.g., 'add')
            operand1: First operand as string
            operand2: Second operand as string
        """
        self.calculator = calculator
        self.operation_name = operation_name
        self.operand1 = operand1
        self.operand2 = operand2
        self.timestamp = datetime.now()
        self.result: Optional[Decimal] = None
    
    def execute(self) -> Optional[Decimal]:
        """
        Execute the calculation command.
        
        Returns:
            Result of the calculation, or None if execution failed
        """
        try:
            operation = OperationFactory.create_operation(self.operation_name)
            self.calculator.set_operation(operation)
            self.result = self.calculator.perform_operation(self.operand1, self.operand2)
            logging.info(f"Command executed: {self.get_description()}")
            return self.result
        except Exception as e:
            logging.error(f"Command execution failed: {e}")
            raise
    
    def get_description(self) -> str:
        """Get description of the command."""
        result_str = f" = {self.result}" if self.result is not None else ""
        return f"{self.operation_name}({self.operand1}, {self.operand2}){result_str}"
    
    def __str__(self) -> str:
        """String representation of command."""
        return f"CalculationCommand({self.get_description()})"


class CommandHistory:
    """
    Maintains history of executed commands.
    
    Allows for command replay, logging, and analysis of user actions.
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize command history.
        
        Args:
            max_size: Maximum number of commands to keep in history
        """
        self.commands: List[Command] = []
        self.max_size = max_size
    
    def add_command(self, command: Command) -> None:
        """
        Add a command to history.
        
        Args:
            command: Command to add
        """
        self.commands.append(command)
        
        # Maintain max size
        if len(self.commands) > self.max_size:
            self.commands.pop(0)
    
    def get_commands(self) -> List[Command]:
        """Get all commands in history."""
        return self.commands.copy()
    
    def get_last_command(self) -> Optional[Command]:
        """Get the most recent command."""
        return self.commands[-1] if self.commands else None
    
    def clear(self) -> None:
        """Clear all commands from history."""
        self.commands.clear()
        logging.info("Command history cleared")
    
    def get_summary(self) -> str:
        """
        Get summary of command history.
        
        Returns:
            Formatted string with command history summary
        """
        if not self.commands:
            return "No commands in history"
        
        lines = [f"Command History ({len(self.commands)} commands):"]
        for i, cmd in enumerate(self.commands, 1):
            lines.append(f"{i}. {cmd.get_description()}")
        
        return "\n".join(lines)


class CommandInvoker:
    """
    Invoker class that executes commands and maintains command history.
    
    Decouples the requester of an action from the object that performs it.
    """
    
    def __init__(self, calculator: Calculator):
        """
        Initialize command invoker.
        
        Args:
            calculator: Calculator instance for executing commands
        """
        self.calculator = calculator
        self.command_history = CommandHistory()
    
    def execute_calculation(self, operation_name: str, 
                          operand1: str, operand2: str) -> Optional[Decimal]:
        """
        Create and execute a calculation command.
        
        Args:
            operation_name: Name of operation to execute
            operand1: First operand
            operand2: Second operand
            
        Returns:
            Result of calculation, or None if failed
        """
        command = CalculationCommand(self.calculator, operation_name, operand1, operand2)
        result = command.execute()
        self.command_history.add_command(command)
        return result
    
    def get_command_history(self) -> CommandHistory:
        """Get the command history."""
        return self.command_history
    
    def show_command_summary(self) -> str:
        """Get formatted command history summary."""
        return self.command_history.get_summary()
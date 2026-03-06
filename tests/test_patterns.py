"""Tests for Decorator and Command patterns."""

import pytest
from decimal import Decimal
from app.decorators import OperationRegistry
from app.calculator import Calculator
from app.commands import (
    Command, CalculationCommand, CommandHistory, CommandInvoker
)

class TestOperationRegistry:
    """Test Decorator pattern for operation registration."""
    
    def test_get_operations(self):
        """Test getting all registered operations."""
        ops = OperationRegistry.get_operations()
        assert 'add' in ops
        assert 'subtract' in ops
        assert 'multiply' in ops
        assert len(ops) >= 10  # All 10 operations should be registered
    
    def test_get_operation_names(self):
        """Test getting list of operation names."""
        names = OperationRegistry.get_operation_names()
        assert 'add' in names
        assert 'divide' in names
        assert isinstance(names, list)
    
    def test_get_by_category(self):
        """Test grouping operations by category."""
        categories = OperationRegistry.get_by_category()
        assert 'Basic Arithmetic' in categories
        assert 'Advanced Operations' in categories
        assert 'Specialized Operations' in categories
        
        # Check that operations are in correct categories
        basic_ops = [op['name'] for op in categories['Basic Arithmetic']]
        assert 'add' in basic_ops
        assert 'subtract' in basic_ops
    
    def test_generate_help_text(self):
        """Test dynamic help menu generation."""
        help_text = OperationRegistry.generate_help_text()
        assert 'Available commands' in help_text
        assert 'add' in help_text
        assert 'Basic Arithmetic' in help_text
        assert 'History Management' in help_text
        assert isinstance(help_text, str)
    
    def test_operation_metadata(self):
        """Test that operations have proper metadata."""
        ops = OperationRegistry.get_operations()
        add_op = ops['add']
        assert add_op['category'] == 'Basic Arithmetic'
        assert add_op['description'] == 'Addition of two numbers'
        assert 'class' in add_op
        assert 'name' in add_op

class TestCalculationCommand:
    """Test Command pattern for calculations."""
    
    @pytest.fixture
    def calculator(self):
        """Provide a fresh calculator instance."""
        return Calculator()
    
    def test_command_creation(self, calculator):
        """Test creating a calculation command."""
        cmd = CalculationCommand(calculator, 'add', '5', '3')
        assert cmd.operation_name == 'add'
        assert cmd.operand1 == '5'
        assert cmd.operand2 == '3'
        assert cmd.result is None  # Not executed yet
    
    def test_command_execution(self, calculator):
        """Test executing a calculation command."""
        cmd = CalculationCommand(calculator, 'add', '5', '3')
        result = cmd.execute()
        assert result == Decimal('8')
        assert cmd.result == Decimal('8')
    
    def test_command_description(self, calculator):
        """Test command description generation."""
        cmd = CalculationCommand(calculator, 'multiply', '4', '5')
        cmd.execute()
        description = cmd.get_description()
        assert 'multiply' in description
        assert '4' in description
        assert '5' in description
        assert '20' in description
    
    def test_command_string_representation(self, calculator):
        """Test command string representation."""
        cmd = CalculationCommand(calculator, 'subtract', '10', '3')
        str_repr = str(cmd)
        assert 'CalculationCommand' in str_repr
        assert 'subtract' in str_repr


class TestCommandHistory:
    """Test command history management."""
    
    @pytest.fixture
    def calculator(self):
        """Provide a fresh calculator instance."""
        return Calculator()
    
    def test_add_command(self, calculator):
        """Test adding commands to history."""
        history = CommandHistory()
        cmd1 = CalculationCommand(calculator, 'add', '5', '3')
        cmd2 = CalculationCommand(calculator, 'multiply', '4', '2')
        
        history.add_command(cmd1)
        history.add_command(cmd2)
        
        assert len(history.get_commands()) == 2
    
    def test_get_last_command(self, calculator):
        """Test retrieving the last command."""
        history = CommandHistory()
        cmd1 = CalculationCommand(calculator, 'add', '5', '3')
        cmd2 = CalculationCommand(calculator, 'subtract', '10', '3')
        
        history.add_command(cmd1)
        history.add_command(cmd2)
        
        last_cmd = history.get_last_command()
        assert last_cmd == cmd2
    
    def test_clear_history(self, calculator):
        """Test clearing command history."""
        history = CommandHistory()
        cmd = CalculationCommand(calculator, 'add', '5', '3')
        history.add_command(cmd)
        
        assert len(history.get_commands()) == 1
        history.clear()
        assert len(history.get_commands()) == 0
    
    def test_max_size_limit(self, calculator):
        """Test that history respects max size."""
        history = CommandHistory(max_size=3)
        
        for i in range(5):
            cmd = CalculationCommand(calculator, 'add', str(i), '1')
            history.add_command(cmd)
        
        assert len(history.get_commands()) == 3  # Should only keep last 3
    
    def test_get_summary(self, calculator):
        """Test command history summary generation."""
        history = CommandHistory()
        cmd1 = CalculationCommand(calculator, 'add', '5', '3')
        cmd1.execute()
        
        history.add_command(cmd1)
        summary = history.get_summary()
        
        assert 'Command History' in summary
        assert 'add' in summary
    
    def test_empty_history_summary(self):
        """Test summary for empty history."""
        history = CommandHistory()
        summary = history.get_summary()
        assert 'No commands' in summary


class TestCommandInvoker:
    """Test CommandInvoker class."""
    
    @pytest.fixture
    def calculator(self):
        """Provide a fresh calculator instance."""
        return Calculator()
    
    def test_invoker_creation(self, calculator):
        """Test creating command invoker."""
        invoker = CommandInvoker(calculator)
        assert invoker.calculator == calculator
        assert invoker.command_history is not None
    
    def test_execute_calculation(self, calculator):
        """Test executing calculation through invoker."""
        invoker = CommandInvoker(calculator)
        result = invoker.execute_calculation('add', '10', '5')
        
        assert result == Decimal('15')
        assert len(invoker.command_history.get_commands()) == 1
    
    def test_multiple_calculations(self, calculator):
        """Test executing multiple calculations."""
        invoker = CommandInvoker(calculator)
        
        invoker.execute_calculation('add', '5', '3')
        invoker.execute_calculation('multiply', '4', '2')
        invoker.execute_calculation('subtract', '10', '3')
        
        assert len(invoker.command_history.get_commands()) == 3
    
    def test_command_summary(self, calculator):
        """Test getting command summary from invoker."""
        invoker = CommandInvoker(calculator)
        invoker.execute_calculation('add', '5', '3')
        
        summary = invoker.show_command_summary()
        assert 'Command History' in summary
        assert '1 commands' in summary
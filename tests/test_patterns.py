"""Tests for Decorator and Command patterns."""

import pytest
from decimal import Decimal
from app.decorators import OperationRegistry
from app.calculator import Calculator


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
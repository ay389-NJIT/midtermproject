########################
# Operation Classes    #
########################

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict
from app.exceptions import ValidationError
from app.decorators import OperationRegistry


class Operation(ABC):
    """Abstract base class for calculator operations."""

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Execute the operation."""
        pass

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Validate operands. Override in subclasses if needed."""
        pass

    def __str__(self) -> str:
        """Return operation name."""
        return self.__class__.__name__

@OperationRegistry.register('add', 'Basic Arithmetic', 'Addition of two numbers', 'add 5 3 = 8')
class Addition(Operation):
    """Addition operation."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a + b

@OperationRegistry.register('subtract', 'Basic Arithmetic', 'Subtraction of two numbers', 'subtract 10 3 = 7')
class Subtraction(Operation):
    """Subtraction operation."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a - b

@OperationRegistry.register('multiply', 'Basic Arithmetic', 'Multiplication of two numbers', 'multiply 4 5 = 20')
class Multiplication(Operation):
    """Multiplication operation."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a * b

@OperationRegistry.register('divide', 'Basic Arithmetic', 'Division of two numbers', 'divide 10 2 = 5')
class Division(Operation):
    """Division operation."""

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Division by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a / b

@OperationRegistry.register('power', 'Advanced Operations', 'Raise number to a power', 'power 2 3 = 8')
class Power(Operation):
    """Power operation."""

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b < 0:
            raise ValidationError("Negative exponents not supported")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(pow(float(a), float(b)))

@OperationRegistry.register('root', 'Advanced Operations', 'Calculate nth root of a number', 'root 27 3 = 3')
class Root(Operation):
    """Root operation."""

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if a < 0:
            raise ValidationError("Cannot calculate root of negative number")
        if b == 0:
            raise ValidationError("Zero root is undefined")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(pow(float(a), 1 / float(b)))

@OperationRegistry.register('modulus', 'Specialized Operations', 'Calculate remainder after division', 'modulus 10 3 = 1')
class Modulus(Operation):
    """Modulus operation (remainder)."""

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Cannot calculate modulus with zero divisor")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a % b

@OperationRegistry.register('int_divide', 'Specialized Operations', 'Integer division (quotient only)', 'int_divide 10 3 = 3')
class IntegerDivision(Operation):
    """Integer division operation."""

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Cannot divide by zero")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a // b

@OperationRegistry.register('percent', 'Specialized Operations', 'Calculate percentage', 'percent 25 100 = 25')
class Percentage(Operation):
    """Percentage calculation ((a/b) * 100)."""

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Cannot calculate percentage with zero base")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return (a / b) * 100

@OperationRegistry.register('abs_diff', 'Specialized Operations', 'Absolute difference between numbers', 'abs_diff 3 10 = 7')
class AbsoluteDifference(Operation):
    """Absolute difference operation."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return abs(a - b)


class OperationFactory:
    """Factory for creating operation instances."""

    _operations: Dict[str, type] = {
        'add': Addition,
        'subtract': Subtraction,
        'multiply': Multiplication,
        'divide': Division,
        'power': Power,
        'root': Root,
        'modulus': Modulus,
        'int_divide': IntegerDivision,
        'percent': Percentage,
        'abs_diff': AbsoluteDifference,
    }

    @classmethod
    def register_operation(cls, name: str, operation_class: type) -> None:
        """Register a new operation type."""
        if not issubclass(operation_class, Operation):
            raise TypeError("Operation class must inherit from Operation")
        cls._operations[name.lower()] = operation_class

    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        """Create an operation instance."""
        operation_class = cls._operations.get(operation_type.lower())
        if not operation_class:
            raise ValueError(f"Unknown operation: {operation_type}")
        return operation_class()
    
    @classmethod
    def get_operation_names(cls) -> list:
        """Get list of all registered operation names."""
        return list(cls._operations.keys())
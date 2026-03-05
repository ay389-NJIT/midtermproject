import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory
from app.calculator_memento import CalculatorMemento


# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        # Patch properties to use the temporary directory paths
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            # Set return values to use paths within the temporary directory
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            # Return an instance of Calculator with the mocked config
            yield Calculator(config=config)

# Test Calculator Initialization

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

# Test Logging Setup

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        
        # Instantiate calculator to trigger logging
        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

# Test Adding and Removing Observers

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers

def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

# Test Setting Operations

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

# Test Performing Operations

def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')

def test_perform_operation_modulus(calculator):
    operation = OperationFactory.create_operation('modulus')
    calculator.set_operation(operation)
    result = calculator.perform_operation(10, 3)
    assert result == Decimal('1')

def test_perform_operation_int_divide(calculator):
    operation = OperationFactory.create_operation('int_divide')
    calculator.set_operation(operation)
    result = calculator.perform_operation(10, 3)
    assert result == Decimal('3')

def test_perform_operation_percent(calculator):
    operation = OperationFactory.create_operation('percent')
    calculator.set_operation(operation)
    result = calculator.perform_operation(25, 100)
    assert result == Decimal('25')

def test_perform_operation_abs_diff(calculator):
    operation = OperationFactory.create_operation('abs_diff')
    calculator.set_operation(operation)
    result = calculator.perform_operation(3, 10)
    assert result == Decimal('7')

def test_perform_operation_validation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)

def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)

# Test Undo/Redo Functionality

def test_undo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []

def test_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1

# Test History Management

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    # Mock CSV data to match the expected format in from_dict
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    
    # Test the load_history functionality
    try:
        calculator.load_history()
        # Verify history length after loading
        assert len(calculator.history) == 1
        # Verify the loaded values
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1 == Decimal("2")
        assert calculator.history[0].operand2 == Decimal("3")
        assert calculator.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")
        
            
# Test Clearing History

def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

def test_undo_redo_empty_stacks(calculator):
    assert calculator.undo() is False
    assert calculator.redo() is False

def test_load_history_file_not_found(calculator):
    with patch('pandas.read_csv', side_effect=FileNotFoundError):
        calculator.load_history() 
        assert calculator.history == []

def test_save_history_permission_error(calculator):
    with patch('pandas.DataFrame.to_csv', side_effect=PermissionError("Permission denied")):
        # Match the actual string from calculator.py: "Failed to save history: ..."
        with pytest.raises(OperationError, match="Failed to save history: Permission denied"):
            calculator.save_history()

def test_memento_to_dict_empty():
    memento = CalculatorMemento(history=[])
    data = memento.to_dict()
    assert data['history'] == []
    assert 'timestamp' in data

def test_memento_from_dict_invalid_date():
    data = {'history': [], 'timestamp': 'invalid-date'}
    with pytest.raises(ValueError):
        CalculatorMemento.from_dict(data)

def test_setup_logging_failure():
    with patch('logging.basicConfig', side_effect=Exception("Log setup failed")):
        with pytest.raises(Exception, match="Log setup failed"):
            calc = Calculator()
            calc._setup_logging()

def test_undo_redo_failure_branches(calculator):
    calculator.undo_stack.clear()
    assert calculator.undo() is False
    calculator.redo_stack.clear()
    assert calculator.redo() is False

def test_save_history_permission_error(calculator):
    with patch('pandas.DataFrame.to_csv', side_effect=PermissionError("Permission denied")):
        # Match the actual string: "Failed to save history: Permission denied"
        with pytest.raises(OperationError, match="Failed to save history: Permission denied"):
            calculator.save_history()

# Test REPL Commands (using patches for input/output handling) - UPDATED FOR COLORAMA

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        # Check for color-coded output using 'in' to match ANSI codes
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("History saved successfully" in call for call in calls)
        assert any("Goodbye" in call for call in calls)

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calculator_repl()
    calls = [str(call) for call in mock_print.call_args_list]
    assert any("Available commands" in call for call in calls)

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    calls = [str(call) for call in mock_print.call_args_list]
    assert any("Result: 5" in call for call in calls)

@patch('builtins.input', side_effect=['modulus', '10', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_modulus(mock_print, mock_input):
    calculator_repl()
    calls = [str(call) for call in mock_print.call_args_list]
    assert any("Result: 1" in call for call in calls)

@patch('builtins.input', side_effect=['int_divide', '10', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_int_divide(mock_print, mock_input):
    calculator_repl()
    calls = [str(call) for call in mock_print.call_args_list]
    assert any("Result: 3" in call for call in calls)

@patch('builtins.input', side_effect=['percent', '25', '100', 'exit'])
@patch('builtins.print')
def test_calculator_repl_percent(mock_print, mock_input):
    calculator_repl()
    calls = [str(call) for call in mock_print.call_args_list]
    assert any("Result: 25" in call for call in calls)

@patch('builtins.input', side_effect=['abs_diff', '3', '10', 'exit'])
@patch('builtins.print')
def test_calculator_repl_abs_diff(mock_print, mock_input):
    calculator_repl()
    calls = [str(call) for call in mock_print.call_args_list]
    assert any("Result: 7" in call for call in calls)

@patch('builtins.input')
def test_repl_keyboard_interrupt(mock_input, capsys):
    mock_input.side_effect = [KeyboardInterrupt, 'exit']
    calculator_repl()
    captured = capsys.readouterr()
    assert "Operation cancelled" in captured.out

@patch('builtins.input')
def test_repl_eof_error(mock_input, capsys):
    mock_input.side_effect = EOFError
    calculator_repl()
    captured = capsys.readouterr()
    assert "Input terminated" in captured.out

@patch('builtins.input', side_effect=['history', 'undo', 'redo', 'clear', 'exit'])
def test_repl_history_commands(mock_input, capsys):
    calculator_repl()
    captured = capsys.readouterr()
    assert "History" in captured.out or "History cleared" in captured.out

@patch('builtins.input', side_effect=['add', 'abc', '3', 'exit'])
def test_repl_validation_error_flow(mock_input, capsys):
    calculator_repl()
    captured = capsys.readouterr()
    assert "Error:" in captured.out

@patch('builtins.input')
def test_repl_comprehensive_flow(mock_input, capsys, calculator):
    mock_input.side_effect = [
        'history',    # Line 61-68
        'clear',      # Line 72-74
        'undo',       # Line 78-82
        'redo',       # Line 86-90
        'save',       # Line 94-99
        'load',       # Line 103-108
        'add', 'cancel', # Line 116-117
        'add', '5', 'cancel', # Line 120-121
        'bad_command', # Line 144
        'exit'        # Exit loop
    ]
    
    with patch('app.calculator_repl.Calculator', return_value=calculator):
        calculator_repl()
    
    out = capsys.readouterr().out
    assert "History cleared" in out
    assert "Operation cancelled" in out
    assert "Unknown command: 'bad_command'" in out

@patch('builtins.input', side_effect=[KeyboardInterrupt, EOFError])
def test_repl_interrupts(mock_input, capsys, calculator):
    with patch('app.calculator_repl.Calculator', return_value=calculator):
        calculator_repl()
    
    out = capsys.readouterr().out
    assert "Operation cancelled" in out
    assert "Input terminated" in out

@patch('builtins.input')
def test_repl_success_and_error_branches(mock_input, capsys, calculator):
    mock_input.side_effect = [
        'add', '1', '1', 'undo', 'redo', 
        'save', 'load', 
        'add', 'invalid', 'invalid', # triggers unexpected if mocked
        'exit'
    ]
    
    with patch('app.calculator_repl.Calculator', return_value=calculator):
        with patch.object(calculator, 'save_history', side_effect=Exception("Save error")):
            with patch.object(calculator, 'load_history', side_effect=Exception("Load error")):
                calculator_repl()
    
    out = capsys.readouterr().out
    assert "Operation undone" in out
    assert "Operation redone" in out
    assert "Error saving history: Save error" in out
    assert "Error loading history: Load error" in out
    assert "Warning: Could not save history: Save error" in out

@patch('app.calculator_repl.Calculator', side_effect=Exception("Fatal Startup Error"))
def test_repl_fatal_error(mock_calc):
    with pytest.raises(Exception, match="Fatal Startup Error"):
        calculator_repl()
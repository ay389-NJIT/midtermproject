# Advanced Calculator Application - Midterm Project
- This calculator is a command-line calculator through the user-selected IDE's terminal, utilizing design patterns, automated testing, and CI/CD integration. Preferred IDE to use is VS Code, for best results.


# Project Description
**Overview**
- The Advanced Calculator Application is command-line tool using Python for development. The calcultor is developed using professional software techniques and includes design patterns such as Factory, Memento, and Observer. There are 10 total arithmetic operations, undo/redo functionality, automated testing, automated Github integration, result storage and more.

**Features**
- Arithmetic: Addition, Subtraction, Multiplication, Division, Power, Root, Modulus, Integer Division, Percentage, Absolute Difference
- View, Save, Load, Clear calculation history
- Undo/Redo
- Color-coded interface (GREEN = Sucess, CYAN = info/prompts, YELLOW = warnings, input messages, RED = errors)
- Automatic logging and history save
- Comprehensive test coverage (90%+)
- Automated Github testing via Github Actions

# Installation Instruction
1. Clone Repo
- git clone 'url'
- cd 'repo name'

2. Create Virtual Environment (VENV)
- python -m venv venv
- source venv/bin/activate

3. Install Requirements
- pip install -r requirements.txt
- **if needed, upgrade pip --> pip install --upgrade pip**

4. Create directories for Logs & History
- mkdir logs history

# Configuration Setup
1. Create .env file<br>
**Base Directories**
- CALCULATOR_LOG_DIR=logs
- CALCULATOR_HISTORY_DIR=history<br>
**History Settings**
- CALCULATOR_MAX_HISTORY_SIZE=1000
- CALCULATOR_AUTO_SAVE=true<br>
**Calculation Settings**
- CALCULATOR_PRECISION=10
- CALCULATOR_MAX_INPUT_VALUE=1000000
- CALCULATOR_DEFAULT_ENCODING=utf-8

# Usage Guide
1. Start main calculator
- python main.py

**Arithmetic Options:**
- Add, Subtract, Multiply, Divide, Power, Root, Modulus, Int_Divide, Percent,Abs_Diff

**Other Command Options:**
- History, Clear, Undo, Redo, Save, Load, Help, Exit

# Testing Guide
1. Run Tests<br>
**All tests**
- pytest<br>
**Verbose Tests**
- pytest -v<br>
**Targeted Testing of a file**
- pytest 'specific file name'<br>

2. Run Tests with Coverage<br>
**Coverage Report**
- pytest --cov=app<br>
**HTML Report**
- pytest --cov=app --cov-report=html<br>

3. Viewing Reports<br>
**Terminal**
- pytest --cov=app --cov-report=term<br>
**HTML (macOS)**
- pytest --cov=app --cov-report=html<br>
- open htmlcov/index.html

# CI/CD Information
- Github Actions Workflow is used via a .yml file to automate testing on Github requests. The workflow file is located at .github/workflows/tests.yml

- When in the Github repository, click the 'Actions' tab. There you can view the workflow running in real-time and its' overall status.

# Advanced Design Patterns

**Dynamic Help Menu (Decorator Pattern)**
The calculator uses the Decorator Pattern to automatically register operations, enabling dynamic help menu generation.

**How it works:**
- Each operation class is decorated with @OperationRegistry.register()
- Includes: name, category, description, and example
- Help menu is generated dynamically from registered operations
- Adding new operations automatically updates the help menu

**Usage:**
- help: displays categorized operations dynamically

# Command Pattern
Operations are encapsulated as command objects, enabling advanced features:

**Benefits:**
- Command queuing and history tracking
- Detailed operation logging
- Potential for command replay
- Separation of request from execution

**Architecture:**
- `Command` - Abstract base class
- `CalculationCommand` - Encapsulates calculation requests
- `CommandHistory` - Tracks executed commands
- `CommandInvoker` - Manages command execution




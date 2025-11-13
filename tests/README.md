# wxGTD Test Suite

This directory contains comprehensive unit tests for the non-GUI components of wxGTD.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_datetimeutils.py    # Tests for datetime utilities
├── test_fmt.py              # Tests for formatting functions
├── test_task_logic.py       # Tests for task logic functions
├── test_notebook_logic.py   # Tests for notebook logic
├── test_dicts_logic.py      # Tests for dictionaries logic
├── test_quicktask_logic.py  # Tests for quicktask creation
├── test_model_objects.py    # Tests for database models
├── test_model_enums.py      # Tests for enums and constants
└── test_validators.py       # Tests for validators
```

## Running Tests

### Using the test runner script (recommended):

**Windows:**
```bash
run_tests.bat
```

**Linux/Mac:**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

**Python:**
```bash
python run_tests.py
```

### Using pytest directly:

```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run all tests
pytest

# Run with coverage
pytest --cov=wxgtd --cov-report=html

# Run specific test file
pytest tests/test_task_logic.py

# Run specific test class
pytest tests/test_task_logic.py::TestAlarmPatternToTime

# Run specific test
pytest tests/test_task_logic.py::TestAlarmPatternToTime::test_day_pattern

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

## Test Coverage

To generate a coverage report:

```bash
pytest --cov=wxgtd --cov-report=html
```

Open `htmlcov/index.html` in your browser to view the detailed coverage report.

## Test Organization

### Logic Tests
- `test_task_logic.py` - Tests for task manipulation functions (repeat, alarm, hide patterns)
- `test_notebook_logic.py` - Tests for notebook page operations
- `test_dicts_logic.py` - Tests for dictionary item management (goals, folders, contexts)
- `test_quicktask_logic.py` - Tests for quick task creation

### Model Tests
- `test_model_objects.py` - Tests for database models and ORM functionality
- `test_model_enums.py` - Tests for constants and enumerations

### Library Tests
- `test_datetimeutils.py` - Tests for datetime conversion utilities
- `test_fmt.py` - Tests for formatting functions

### Validator Tests
- `test_validators.py` - Tests for input validators (length, format, etc.)

## Fixtures

Common fixtures are defined in `conftest.py`:

- `db_session` - In-memory SQLite database session
- `mock_publisher` - Mocked event publisher for testing without GUI
- `sample_task` - Pre-created task for testing
- `sample_project` - Pre-created project for testing
- `sample_checklist` - Pre-created checklist for testing

## Writing New Tests

When adding new tests:

1. Place test files in the `tests/` directory
2. Name test files with `test_` prefix
3. Name test classes with `Test` prefix
4. Name test functions with `test_` prefix
5. Use descriptive docstrings for test cases
6. Use appropriate fixtures from `conftest.py`
7. Mock external dependencies (GUI, file system, network)

Example:

```python
def test_feature_description():
    """Test that feature works correctly."""
    # Arrange
    input_value = "test"
    
    # Act
    result = function_to_test(input_value)
    
    # Assert
    assert result == expected_value
```

## Dependencies

Test dependencies are listed in `requirements-dev.txt`:

- pytest - Test framework
- pytest-cov - Coverage plugin
- pytest-mock - Mocking utilities
- freezegun - Time mocking for date/time tests

## Continuous Integration

Tests should pass before merging code. Run the full test suite:

```bash
pytest --cov=wxgtd --cov-report=term-missing
```

Target coverage: >80% for non-GUI code.

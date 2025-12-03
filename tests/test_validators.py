#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Tests for wxgtd.wxtools.validators module.

Copyright (c) Karol Będkowski, 2013-2014
Copyright (c) Johan Andersson, 2025
Copyright (c) Johan Andersson, 2025
License: GPLv2+
"""

import pytest
from wxgtd.wxtools.validators._simple_validator import SimpleValidator
from wxgtd.wxtools.validators.errors import ValidateError
from wxgtd.wxtools.validators.v_length import (
    NotEmptyValidator, MinLenValidator, MaxLenValidator
)


class TestSimpleValidator:
    """Tests for SimpleValidator base class."""
    
    def test_error_property(self):
        """Test error property returns error message."""
        validator = SimpleValidator(error_message="Test error")
        assert validator.error == "Test error"
    
    def test_value_from_window_passthrough(self):
        """Test value_from_window passes value through."""
        validator = SimpleValidator()
        assert validator.value_from_window("test") == "test"
        assert validator.value_from_window(123) == 123
    
    def test_value_to_window_passthrough(self):
        """Test value_to_window passes value through."""
        validator = SimpleValidator()
        assert validator.value_to_window("test") == "test"
        assert validator.value_to_window(123) == 123
    
    def test_raise_error(self):
        """Test _raise_error raises ValidateError."""
        validator = SimpleValidator(error_message="Error occurred")
        with pytest.raises(ValidateError):
            validator._raise_error()


class TestNotEmptyValidator:
    """Tests for NotEmptyValidator."""
    
    def test_valid_string(self):
        """Test valid non-empty string."""
        validator = NotEmptyValidator()
        result = validator.value_from_window("test")
        assert result == "test"
    
    def test_empty_string_raises_error(self):
        """Test empty string raises ValidateError."""
        validator = NotEmptyValidator()
        with pytest.raises(ValidateError):
            validator.value_from_window("")
    
    def test_none_raises_error(self):
        """Test None raises ValidateError."""
        validator = NotEmptyValidator()
        with pytest.raises(ValidateError):
            validator.value_from_window(None)
    
    def test_strip_whitespace(self):
        """Test stripping whitespace when strip=True."""
        validator = NotEmptyValidator(strip=True)
        result = validator.value_from_window("  test  ")
        assert result == "test"
    
    def test_strip_empty_after_strip_raises_error(self):
        """Test empty string after stripping raises error."""
        validator = NotEmptyValidator(strip=True)
        with pytest.raises(ValidateError):
            validator.value_from_window("   ")
    
    def test_no_strip_preserves_whitespace(self):
        """Test whitespace is preserved when strip=False."""
        validator = NotEmptyValidator(strip=False)
        result = validator.value_from_window("  test  ")
        assert result == "  test  "
    
    def test_custom_error_message(self):
        """Test custom error message."""
        custom_msg = "Custom error message"
        validator = NotEmptyValidator(error_message=custom_msg)
        assert validator.error == custom_msg


class TestMinLenValidator:
    """Tests for MinLenValidator."""
    
    def test_valid_length(self):
        """Test string with valid length."""
        validator = MinLenValidator(min_len=3)
        result = validator.value_from_window("test")
        assert result == "test"
    
    def test_exact_min_length(self):
        """Test string with exact minimum length."""
        validator = MinLenValidator(min_len=4)
        result = validator.value_from_window("test")
        assert result == "test"
    
    def test_too_short_raises_error(self):
        """Test too short string raises ValidateError."""
        validator = MinLenValidator(min_len=5)
        with pytest.raises(ValidateError):
            validator.value_from_window("test")
    
    def test_empty_string_raises_error(self):
        """Test empty string raises ValidateError."""
        validator = MinLenValidator(min_len=1)
        with pytest.raises(ValidateError):
            validator.value_from_window("")
    
    def test_none_value(self):
        """Test None value is converted to empty string."""
        validator = MinLenValidator(min_len=0)
        result = validator.value_from_window(None)
        assert result == ""
    
    def test_custom_error_message(self):
        """Test custom error message."""
        custom_msg = "String too short"
        validator = MinLenValidator(min_len=5, error_message=custom_msg)
        assert validator.error == custom_msg


class TestMaxLenValidator:
    """Tests for MaxLenValidator."""
    
    def test_valid_length(self):
        """Test string with valid length."""
        validator = MaxLenValidator(max_len=10)
        result = validator.value_from_window("test")
        assert result == "test"
    
    def test_exact_max_length(self):
        """Test string with exact maximum length."""
        validator = MaxLenValidator(max_len=4)
        result = validator.value_from_window("test")
        assert result == "test"
    
    def test_too_long_raises_error(self):
        """Test too long string raises ValidateError."""
        validator = MaxLenValidator(max_len=3)
        with pytest.raises(ValidateError):
            validator.value_from_window("test")
    
    def test_empty_string(self):
        """Test empty string is valid."""
        validator = MaxLenValidator(max_len=5)
        result = validator.value_from_window("")
        assert result == ""
    
    def test_custom_error_message(self):
        """Test custom error message."""
        custom_msg = "String too long"
        validator = MaxLenValidator(max_len=5, error_message=custom_msg)
        assert validator.error == custom_msg


class TestValidatorChaining:
    """Tests for chaining multiple validators."""
    
    def test_not_empty_and_min_length(self):
        """Test chaining NotEmptyValidator and MinLenValidator."""
        validators = [NotEmptyValidator(strip=True), MinLenValidator(min_len=3)]
        
        # Valid value
        value = "  test  "
        for validator in validators:
            value = validator.value_from_window(value)
        assert value == "test"
    
    def test_not_empty_and_max_length(self):
        """Test chaining NotEmptyValidator and MaxLenValidator."""
        validators = [NotEmptyValidator(), MaxLenValidator(max_len=5)]
        
        # Valid value
        value = "test"
        for validator in validators:
            value = validator.value_from_window(value)
        assert value == "test"
        
        # Invalid - too long
        validators = [NotEmptyValidator(), MaxLenValidator(max_len=2)]
        with pytest.raises(ValidateError):
            value = "test"
            for validator in validators:
                value = validator.value_from_window(value)
    
    def test_min_and_max_length(self):
        """Test chaining MinLenValidator and MaxLenValidator."""
        validators = [MinLenValidator(min_len=3), MaxLenValidator(max_len=10)]
        
        # Valid value
        value = "test"
        for validator in validators:
            value = validator.value_from_window(value)
        assert value == "test"
        
        # Invalid - too short
        validators = [MinLenValidator(min_len=5), MaxLenValidator(max_len=10)]
        with pytest.raises(ValidateError):
            value = "test"
            for validator in validators:
                value = validator.value_from_window(value)
        
        # Invalid - too long
        validators = [MinLenValidator(min_len=1), MaxLenValidator(max_len=3)]
        with pytest.raises(ValidateError):
            value = "testing"
            for validator in validators:
                value = validator.value_from_window(value)


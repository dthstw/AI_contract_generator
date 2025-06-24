import pytest
from agent_ai.cli import number_of_words_validator, non_empty_string
import argparse

# number_of_words_validator

def test_number_of_words_valid():
    assert number_of_words_validator("100") == 100

def test_number_of_words_too_small():
    with pytest.raises(argparse.ArgumentTypeError, match="must be greater than 25"):
        number_of_words_validator("10")

def test_number_of_words_not_integer():
    with pytest.raises(argparse.ArgumentTypeError, match="must be an integer"):
        number_of_words_validator("abc")


# non_empty_string

def test_non_empty_string_valid():
    assert non_empty_string("LayerX") == "LayerX"

def test_non_empty_string_empty():
    with pytest.raises(argparse.ArgumentTypeError, match="cannot be empty"):
        non_empty_string("")

def test_non_empty_string_whitespace():
    with pytest.raises(argparse.ArgumentTypeError, match="cannot be empty"):
        non_empty_string("   ")

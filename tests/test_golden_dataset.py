"""
Pytest test suite for validating fonemas transcription against golden dataset.

This test suite loads the golden dataset and runs comparison tests to ensure
the current implementation produces consistent results.

Usage:
    pytest tests/test_golden_dataset.py
    pytest tests/test_golden_dataset.py -v  # verbose
    pytest tests/test_golden_dataset.py -k "test_transcription"  # specific test
"""

import json
import pytest
from pathlib import Path
from fonemas import Transcription


# Load golden dataset once for all tests
@pytest.fixture(scope="module")
def golden_data():
    """Load the golden dataset from JSON file."""
    golden_path = Path(__file__).parent / "golden_data.json"

    if not golden_path.exists():
        pytest.skip(
            f"Golden dataset not found at {golden_path}. "
            "Run 'python golden_dataset.py generate' first."
        )

    with open(golden_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Filter out entries with errors
    valid_data = [entry for entry in data if "error" not in entry]
    return valid_data


def transcribe_sentence(sentence: str):
    """Helper function to transcribe a sentence."""
    t = Transcription(sentence)
    return {
        "phonology": {
            "words": t.phonology.words,
            "syllables": t.phonology.syllables
        },
        "phonetics": {
            "words": t.phonetics.words,
            "syllables": t.phonetics.syllables
        },
        "sampa": {
            "words": t.sampa.words,
            "syllables": t.sampa.syllables
        }
    }


@pytest.mark.parametrize("entry", [pytest.param(entry, id=f"{i:03d}_{entry['input'][:50]}")
                                     for i, entry in enumerate(json.load(open(
                                         Path(__file__).parent / "golden_data.json", 'r'))
                                         if (Path(__file__).parent / "golden_data.json").exists()
                                         else [], 1)
                                     if "error" not in entry])
def test_transcription_matches_golden(entry):
    """Test that transcription matches the golden dataset for each sentence."""
    sentence = entry["input"]
    expected = entry

    # Transcribe the sentence
    actual = transcribe_sentence(sentence)

    # Compare phonology
    assert actual["phonology"]["words"] == expected["phonology"]["words"], \
        f"Phonology words mismatch for: {sentence}"
    assert actual["phonology"]["syllables"] == expected["phonology"]["syllables"], \
        f"Phonology syllables mismatch for: {sentence}"

    # Compare phonetics
    assert actual["phonetics"]["words"] == expected["phonetics"]["words"], \
        f"Phonetics words mismatch for: {sentence}"
    assert actual["phonetics"]["syllables"] == expected["phonetics"]["syllables"], \
        f"Phonetics syllables mismatch for: {sentence}"

    # Compare SAMPA
    assert actual["sampa"]["words"] == expected["sampa"]["words"], \
        f"SAMPA words mismatch for: {sentence}"
    assert actual["sampa"]["syllables"] == expected["sampa"]["syllables"], \
        f"SAMPA syllables mismatch for: {sentence}"


def test_golden_dataset_exists():
    """Test that the golden dataset file exists."""
    golden_path = Path(__file__).parent / "golden_data.json"
    assert golden_path.exists(), \
        f"Golden dataset not found. Run 'python golden_dataset.py generate' first."


def test_golden_dataset_not_empty(golden_data):
    """Test that the golden dataset contains data."""
    assert len(golden_data) > 0, "Golden dataset is empty"


def test_golden_dataset_structure(golden_data):
    """Test that golden dataset entries have the expected structure."""
    for entry in golden_data[:5]:  # Check first 5 entries
        assert "input" in entry, "Entry missing 'input' field"
        assert "phonology" in entry, "Entry missing 'phonology' field"
        assert "phonetics" in entry, "Entry missing 'phonetics' field"
        assert "sampa" in entry, "Entry missing 'sampa' field"

        for section in ['phonology', 'phonetics', 'sampa']:
            assert "words" in entry[section], f"{section} missing 'words' field"
            assert "syllables" in entry[section], f"{section} missing 'syllables' field"
            assert isinstance(entry[section]["words"], list), \
                f"{section}.words should be a list"
            assert isinstance(entry[section]["syllables"], list), \
                f"{section}.syllables should be a list"

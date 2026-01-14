#!/usr/bin/env python3
"""
Golden Dataset Generator and Test Suite for fonemas library

This script generates a golden dataset from the Sharvard corpus and provides
a test framework to validate the fonemas transcription against expected outputs.

Usage:
    # Generate golden dataset (only do this once to establish baseline)
    python golden_dataset.py generate

    # Run tests against golden dataset
    python golden_dataset.py test

    # Run tests with verbose output
    python golden_dataset.py test --verbose
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from fonemas import Transcription


class GoldenDataset:
    """Manages golden dataset generation and testing."""

    def __init__(self, corpus_path: str = "fonemas/sharvard.txt",
                 golden_path: str = "tests/golden_data.json"):
        self.corpus_path = Path(corpus_path)
        self.golden_path = Path(golden_path)

    def read_corpus(self) -> List[str]:
        """Read sentences from the Sharvard corpus, skipping comments and empty lines."""
        sentences = []
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    sentences.append(line)
        return sentences

    def transcribe_sentence(self, sentence: str) -> Dict[str, Any]:
        """
        Transcribe a sentence and return all outputs in a structured format.

        Returns:
            Dict containing input sentence and all transcription outputs
        """
        t = Transcription(sentence)

        return {
            "input": sentence,
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

    def generate_golden_data(self) -> List[Dict[str, Any]]:
        """Generate golden dataset from all sentences in the corpus."""
        sentences = self.read_corpus()
        golden_data = []

        print(f"Processing {len(sentences)} sentences...")
        for i, sentence in enumerate(sentences, 1):
            if i % 50 == 0:
                print(f"  Processed {i}/{len(sentences)} sentences...")

            try:
                result = self.transcribe_sentence(sentence)
                golden_data.append(result)
            except Exception as e:
                print(f"ERROR processing sentence {i}: {sentence}")
                print(f"  Exception: {e}")
                # Store the error in the golden data
                golden_data.append({
                    "input": sentence,
                    "error": str(e)
                })

        print(f"Completed processing {len(sentences)} sentences.")
        return golden_data

    def save_golden_data(self, golden_data: List[Dict[str, Any]]) -> None:
        """Save golden dataset to JSON file."""
        # Ensure the directory exists
        self.golden_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.golden_path, 'w', encoding='utf-8') as f:
            json.dump(golden_data, f, ensure_ascii=False, indent=2)

        print(f"\nGolden dataset saved to: {self.golden_path}")
        print(f"Total entries: {len(golden_data)}")

    def load_golden_data(self) -> List[Dict[str, Any]]:
        """Load golden dataset from JSON file."""
        if not self.golden_path.exists():
            raise FileNotFoundError(
                f"Golden dataset not found at {self.golden_path}. "
                "Run 'python golden_dataset.py generate' first."
            )

        with open(self.golden_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def compare_results(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare expected vs actual transcription results.

        Returns:
            Dict with comparison results including any differences
        """
        differences = {}

        # Compare each section
        for section in ['phonology', 'phonetics', 'sampa']:
            if section not in actual:
                differences[section] = {"error": "Section missing in actual output"}
                continue

            section_diffs = {}
            for key in ['words', 'syllables']:
                expected_val = expected[section][key]
                actual_val = actual[section][key]

                if expected_val != actual_val:
                    section_diffs[key] = {
                        "expected": expected_val,
                        "actual": actual_val
                    }

            if section_diffs:
                differences[section] = section_diffs

        return differences

    def run_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """
        Run tests comparing current code output against golden dataset.

        Args:
            verbose: If True, print details for each test

        Returns:
            Dict with test statistics and failures
        """
        golden_data = self.load_golden_data()

        results = {
            "total": len(golden_data),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "failures": []
        }

        print(f"Running tests against {len(golden_data)} golden dataset entries...\n")

        for i, expected in enumerate(golden_data, 1):
            sentence = expected["input"]

            # Skip entries that had errors during generation
            if "error" in expected:
                results["errors"] += 1
                if verbose:
                    print(f"SKIP [{i}]: {sentence} (error in golden data)")
                continue

            try:
                # Run current code
                actual = self.transcribe_sentence(sentence)

                # Compare results
                differences = self.compare_results(expected, actual)

                if differences:
                    results["failed"] += 1
                    results["failures"].append({
                        "index": i,
                        "sentence": sentence,
                        "differences": differences
                    })
                    if verbose:
                        print(f"FAIL [{i}]: {sentence}")
                        self._print_differences(differences)
                else:
                    results["passed"] += 1
                    if verbose:
                        print(f"PASS [{i}]: {sentence}")

            except Exception as e:
                results["errors"] += 1
                results["failures"].append({
                    "index": i,
                    "sentence": sentence,
                    "error": str(e)
                })
                if verbose:
                    print(f"ERROR [{i}]: {sentence}")
                    print(f"  Exception: {e}")

        return results

    def _print_differences(self, differences: Dict[str, Any], indent: str = "  ") -> None:
        """Pretty print differences between expected and actual results."""
        for section, section_diffs in differences.items():
            print(f"{indent}{section}:")
            if "error" in section_diffs:
                print(f"{indent}  Error: {section_diffs['error']}")
            else:
                for key, diff in section_diffs.items():
                    print(f"{indent}  {key}:")
                    print(f"{indent}    expected: {diff['expected']}")
                    print(f"{indent}    actual:   {diff['actual']}")

    def print_test_summary(self, results: Dict[str, Any]) -> None:
        """Print a summary of test results."""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total tests:  {results['total']}")
        print(f"Passed:       {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
        print(f"Failed:       {results['failed']}")
        print(f"Errors:       {results['errors']}")

        if results['failures']:
            print(f"\n{len(results['failures'])} FAILURES:")
            for failure in results['failures'][:10]:  # Show first 10 failures
                print(f"\n  [{failure['index']}] {failure['sentence']}")
                if 'error' in failure:
                    print(f"    Error: {failure['error']}")
                else:
                    self._print_differences(failure['differences'], indent="    ")

            if len(results['failures']) > 10:
                print(f"\n  ... and {len(results['failures']) - 10} more failures")

        print("="*70)

        # Return exit code
        return 0 if results['failed'] == 0 and results['errors'] == 0 else 1


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()
    dataset = GoldenDataset()

    if command == "generate":
        print("Generating golden dataset from Sharvard corpus...")
        print(f"Reading from: {dataset.corpus_path}")
        golden_data = dataset.generate_golden_data()
        dataset.save_golden_data(golden_data)
        print("\n✓ Golden dataset generated successfully!")
        sys.exit(0)

    elif command == "test":
        verbose = "--verbose" in sys.argv or "-v" in sys.argv
        results = dataset.run_tests(verbose=verbose)
        exit_code = dataset.print_test_summary(results)
        sys.exit(exit_code)

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

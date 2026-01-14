#!/usr/bin/env python3
"""
Command-line interface for the fonemas library.
"""
import argparse
import json
import sys
from fonemas import Transcription


def main():
    parser = argparse.ArgumentParser(
        description='Transcribe Spanish text to IPA phonological and phonetic representations.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Averigüéis"
  %(prog)s "Averigüéis" --structured
  %(prog)s "espíritu" --mono --epenthesis --aspiration
  %(prog)s "México" --structured --format json
        """
    )

    # Positional argument
    parser.add_argument(
        'text',
        type=str,
        help='Spanish text to transcribe'
    )

    # Output format options
    parser.add_argument(
        '-s', '--structured',
        action='store_true',
        help='Output in structured format instead of simple string'
    )

    parser.add_argument(
        '-f', '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format for structured mode (default: text)'
    )

    # Transcription options
    parser.add_argument(
        '--mono',
        action='store_true',
        help='Mark stress on monosyllabic words'
    )

    parser.add_argument(
        '--exceptions',
        type=int,
        choices=[0, 1, 2],
        default=1,
        help='Level of exceptions handling (0: none, 1: basic, 2: extended)'
    )

    parser.add_argument(
        '--epenthesis',
        action='store_true',
        help='Apply epenthesis (add initial "e" before s+consonant clusters)'
    )

    parser.add_argument(
        '--aspiration',
        action='store_true',
        help='Mark aspiration for word-initial "h"'
    )

    parser.add_argument(
        '--rehash',
        action='store_true',
        help='Apply rehashing to redistribute consonants across word boundaries'
    )

    parser.add_argument(
        '--stress',
        type=str,
        default='"',
        help='Character used to mark stress in SAMPA transcription (default: ")'
    )

    args = parser.parse_args()

    # Create transcription
    try:
        transcription = Transcription(
            args.text,
            mono=args.mono,
            exceptions=args.exceptions,
            epenthesis=args.epenthesis,
            aspiration=args.aspiration,
            rehash=args.rehash,
            stress=args.stress
        )
    except Exception as e:
        print(f"Error during transcription: {e}", file=sys.stderr)
        sys.exit(1)

    # Output results
    if args.structured:
        output_structured(transcription, args.format)
    else:
        output_simple(transcription)


def output_simple(transcription):
    """Output transcription in simple string format (default)."""
    print(' '.join(transcription.phonology.words))


def output_structured(transcription, format_type):
    """Output transcription in structured format."""
    data = {
        'phonology': {
            'words': transcription.phonology.words,
            'syllables': transcription.phonology.syllables
        },
        'phonetics': {
            'words': transcription.phonetics.words,
            'syllables': transcription.phonetics.syllables
        },
        'sampa': {
            'words': transcription.sampa.words,
            'syllables': transcription.sampa.syllables
        }
    }

    if format_type == 'json':
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        # Text format
        print("Phonology:")
        print(f"  Words:     {' '.join(data['phonology']['words'])}")
        print(f"  Syllables: {' '.join(data['phonology']['syllables'])}")
        print()
        print("Phonetics:")
        print(f"  Words:     {' '.join(data['phonetics']['words'])}")
        print(f"  Syllables: {' '.join(data['phonetics']['syllables'])}")
        print()
        print("SAMPA:")
        print(f"  Words:     {' '.join(data['sampa']['words'])}")
        print(f"  Syllables: {' '.join(data['sampa']['syllables'])}")


if __name__ == '__main__':
    main()

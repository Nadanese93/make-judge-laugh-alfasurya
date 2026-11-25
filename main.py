"""Write the one-line office joke to MAKEFUN_OUTPUT_DIR/entry.txt.

Reads the MAKEFUN_OUTPUT_DIR environment variable, validates the entry
text against the contest gate (1-200 characters, single line, not blank),
writes it as UTF-8 with no trailing newline, then re-reads the file and
raises if the bytes on disk differ from what was written.
Standard library only; no network; deterministic output.
"""

import os
import sys

ENTRY_TEXT = (
    "My standing desk has been standing for three years. "
    "I have been sitting the whole time."
)

MAX_CHARS = 200


class BlankError(ValueError):
    """Entry text is empty or only whitespace."""


class MultiLineError(ValueError):
    """Entry text contains a line break; the gate requires one line."""


class LengthError(ValueError):
    """Entry text exceeds the 200-character limit."""


def validate(text: str) -> None:
    """Reject content that would fail the contest gate.

    Each failure mode raises its own error type so callers can tell
    exactly which gate rule was violated.
    """
    if not text.strip():
        raise BlankError("entry text is blank or only whitespace")
    if "\n" in text or "\r" in text:
        raise MultiLineError(
            "entry text must be a single line (found a line break)"
        )
    if len(text) > MAX_CHARS:
        raise LengthError(
            "entry text is %d characters, over the %d limit"
            % (len(text), MAX_CHARS)
        )


def verify_written(path: str, expected: bytes) -> None:
    """Re-read path and raise if the bytes differ from expected."""
    with open(path, "rb") as f:
        actual = f.read()
    if actual != expected:
        raise RuntimeError(
            "read-back mismatch for %s: wrote %d bytes, read %d bytes"
            % (path, len(expected), len(actual))
        )


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("error: MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 2

    try:
        validate(ENTRY_TEXT)
    except ValueError as exc:
        print("error: %s: %s" % (type(exc).__name__, exc), file=sys.stderr)
        return 1

    path = os.path.join(out_dir, "entry.txt")
    data = ENTRY_TEXT.encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)

    try:
        verify_written(path, data)
    except (OSError, RuntimeError) as exc:
        print("error: read-back verification failed: %s" % exc, file=sys.stderr)
        return 1

    print("wrote %s (%d bytes, verified)" % (path, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
